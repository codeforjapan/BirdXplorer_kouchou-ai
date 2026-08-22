"""Tests for per-cluster, per-period opinion counts (issue #8 案A scaffolding)."""

import polars as pl

from analysis_core.steps.hierarchical_aggregation import _build_cluster_value_by_period


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
