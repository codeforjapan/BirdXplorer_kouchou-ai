"""Tests for per-cluster, per-period opinion counts (issue #8 案A scaffolding)."""

import json

import polars as pl

from analysis_core.steps.hierarchical_aggregation import _build_cluster_value_by_period, hierarchical_aggregation


class TestHierarchicalAggregationBackwardCompatibility:
    """Regression: existing callers unaware of period_attribute (e.g. the monthly

    report pipeline in codeforjapan/BirdXplorer-cdk, which bundles this package
    via a floating ECR `latest` tag and has no reason to set this new option)
    must see byte-for-byte unchanged behavior from hierarchical_aggregation().
    """

    def _write_fixture_dataset(self, tmp_path):
        output_base_dir = tmp_path / "outputs"
        input_base_dir = tmp_path / "inputs"
        dataset = "test_output"
        (output_base_dir / dataset).mkdir(parents=True)
        input_base_dir.mkdir(parents=True)

        pl.DataFrame({"arg-id": ["A1", "A2"], "argument": ["arg1", "arg2"]}).write_csv(
            output_base_dir / dataset / "args.csv"
        )
        pl.DataFrame({"arg-id": ["A1", "A2"], "comment-id": ["c1", "c2"]}).write_csv(
            output_base_dir / dataset / "relations.csv"
        )
        pl.DataFrame(
            {
                "arg-id": ["A1", "A2"],
                "argument": ["arg1", "arg2"],
                "x": [0.1, 0.2],
                "y": [0.1, 0.2],
                "cluster-level-1-id": ["C1", "C1"],
            }
        ).write_csv(output_base_dir / dataset / "hierarchical_clusters.csv")
        pl.DataFrame(
            {
                "level": [1],
                "id": ["C1"],
                "label": ["Cluster1"],
                "description": ["desc1"],
                "value": [2],
                "parent": ["0"],
                "density_rank_percentile": [50.0],
            }
        ).write_csv(output_base_dir / dataset / "hierarchical_merge_labels.csv")
        (output_base_dir / dataset / "hierarchical_overview.txt").write_text("overview text")
        pl.DataFrame({"comment-id": ["c1", "c2"], "comment-body": ["a", "b"]}).write_csv(
            input_base_dir / "test_input.csv"
        )

        return output_base_dir, input_base_dir, dataset

    def _base_config(self, output_base_dir, input_base_dir, dataset):
        return {
            "input": "test_input",
            "output_dir": dataset,
            "intro": "",
            "extraction": {"limit": 30, "categories": {}},
            "is_pubcom": False,
            "enable_source_link": False,
            "_input_base_dir": str(input_base_dir),
            "_output_base_dir": str(output_base_dir),
        }

    def test_output_unchanged_for_config_without_period_attribute(self, tmp_path):
        """A caller's config with no period_attribute key at all (the pre-#8 shape) must still work and get value_by_period=None everywhere."""
        output_base_dir, input_base_dir, dataset = self._write_fixture_dataset(tmp_path)
        config = self._base_config(output_base_dir, input_base_dir, dataset)
        config["hierarchical_aggregation"] = {"hidden_properties": {}}

        assert hierarchical_aggregation(config) is True

        result = json.loads((output_base_dir / dataset / "hierarchical_result.json").read_text())

        assert [c["value"] for c in result["clusters"]] == [2, 2]
        assert result["clusters"][0]["id"] == "0"
        assert result["clusters"][1]["id"] == "C1"
        for cluster in result["clusters"]:
            assert cluster["value_by_period"] is None
        assert result["comment_num"] == 2

    def test_output_unchanged_when_period_attribute_column_missing(self, tmp_path):
        """period_attribute is set, but the input CSV has no matching attribute_* column: still a no-op, not an error."""
        output_base_dir, input_base_dir, dataset = self._write_fixture_dataset(tmp_path)
        config = self._base_config(output_base_dir, input_base_dir, dataset)
        config["hierarchical_aggregation"] = {"hidden_properties": {}, "period_attribute": "week"}

        assert hierarchical_aggregation(config) is True

        result = json.loads((output_base_dir / dataset / "hierarchical_result.json").read_text())
        for cluster in result["clusters"]:
            assert cluster["value_by_period"] is None


class TestBuildClusterValueByPeriod:
    """Unit tests for _build_cluster_value_by_period."""

    def test_counts_per_cluster_per_period(self):
        """Occurrences are grouped by cluster and period, including a synthetic root ('0') bucket."""
        clusters = pl.DataFrame(
            {
                "arg-id": ["A1", "A2", "A3"],
                "cluster-level-1-id": ["C1", "C1", "C2"],
            }
        )
        relation_df = pl.DataFrame(
            {
                "arg-id": ["A1", "A2", "A3"],
                "comment-id": ["c1", "c2", "c3"],
            }
        )
        comments = pl.DataFrame(
            {
                "comment-id": ["c1", "c2", "c3"],
                "attribute_week": ["2026-W21", "2026-W22", "2026-W21"],
            }
        )

        result = _build_cluster_value_by_period(clusters, relation_df, comments, "attribute_week")

        assert result["C1"] == {"2026-W21": 1, "2026-W22": 1}
        assert result["C2"] == {"2026-W21": 1}
        assert result["0"] == {"2026-W21": 2, "2026-W22": 1}

    def test_deduplicated_argument_counted_once_per_comment_occurrence(self):
        """An argument text deduped into a single arg-id across two comments/weeks

        must be counted in both weeks, not collapsed onto a single comment the way
        the arg_comment_map used in _build_arguments would (see issue #8).
        """
        clusters = pl.DataFrame(
            {
                "arg-id": ["A1"],
                "cluster-level-1-id": ["C1"],
            }
        )
        relation_df = pl.DataFrame(
            {
                "arg-id": ["A1", "A1"],
                "comment-id": ["c1", "c2"],
            }
        )
        comments = pl.DataFrame(
            {
                "comment-id": ["c1", "c2"],
                "attribute_week": ["2026-W21", "2026-W22"],
            }
        )

        result = _build_cluster_value_by_period(clusters, relation_df, comments, "attribute_week")

        assert result["C1"] == {"2026-W21": 1, "2026-W22": 1}
        assert result["0"] == {"2026-W21": 1, "2026-W22": 1}

    def test_missing_period_column_returns_empty_dict(self):
        """No period_attribute configured, or the column doesn't exist -> feature is a no-op."""
        clusters = pl.DataFrame({"arg-id": ["A1"], "cluster-level-1-id": ["C1"]})
        relation_df = pl.DataFrame({"arg-id": ["A1"], "comment-id": ["c1"]})
        comments = pl.DataFrame({"comment-id": ["c1"]})

        assert _build_cluster_value_by_period(clusters, relation_df, comments, None) == {}
        assert _build_cluster_value_by_period(clusters, relation_df, comments, "attribute_week") == {}

    def test_comment_ids_of_different_types_are_matched(self):
        """comment-id may be read as int in one frame and str in another; both sides are cast to Utf8."""
        clusters = pl.DataFrame({"arg-id": ["A1"], "cluster-level-1-id": ["C1"]})
        relation_df = pl.DataFrame({"arg-id": ["A1"], "comment-id": [1]})
        comments = pl.DataFrame({"comment-id": ["1"], "attribute_week": ["2026-W21"]})

        result = _build_cluster_value_by_period(clusters, relation_df, comments, "attribute_week")

        assert result["C1"] == {"2026-W21": 1}
