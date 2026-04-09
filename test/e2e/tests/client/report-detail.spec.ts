import { test, expect } from "@playwright/test";

/**
 * Client - レポート詳細テスト
 *
 * 個別レポート詳細ページ（http://localhost:3000/[slug]）の機能をテストします。
 * ダミーAPIサーバー（port 8002）がテストフィクスチャを返します。
 *
 * 注: BirdXplorer fork では Header/Footer/Overview/BackButton/Reporter を
 * 非表示にしているため、それらの要素に対するテストは含みません。
 * ClientContainer（チャート・クラスタ表示）の動作を検証します。
 */

test.describe("Client - レポート詳細", () => {
  test("正常系 - レポート詳細が表示される", async ({ page }) => {
    await page.goto("/test-report-1");
    await page.waitForLoadState("networkidle");

    // ClientContainerが表示される（チャートエリアが存在する）
    await expect(page.locator("[data-testid='client-container']").or(page.locator(".js-plotly-plot")).or(page.locator("svg")).first()).toBeVisible();
  });

  test("クラスタ情報が表示される", async ({ page }) => {
    await page.goto("/test-report-1");
    await page.waitForLoadState("networkidle");

    // クラスタのラベルが表示される
    await expect(page.getByText(/生成AIと著作権に関する法的/).first()).toBeVisible();
  });

  test("異常系 - 存在しないレポートで404エラーが表示される", async ({ page }) => {
    await page.goto("/non-existent-report");
    await page.waitForLoadState("networkidle");

    // 404ページまたはNot Foundメッセージが表示される
    // Next.jsのnot-found.tsxが表示される
    await expect(page.getByText(/404|Not Found|見つかりません/)).toBeVisible();
  });
});

test.describe("Client - レポート詳細のレスポンシブデザイン", () => {
  const viewports = [
    { name: "デスクトップ", width: 1920, height: 1080 },
    { name: "タブレット", width: 768, height: 1024 },
    { name: "モバイル", width: 375, height: 667 },
  ];

  for (const viewport of viewports) {
    test(`${viewport.name}サイズでレポート詳細が表示される`, async ({ page }) => {
      await page.setViewportSize({ width: viewport.width, height: viewport.height });

      await page.goto("/test-report-1");
      await page.waitForLoadState("networkidle");

      // クラスタ情報が表示される
      await expect(page.getByText(/生成AIと著作権に関する法的/).first()).toBeVisible();
    });
  }
});

test.describe("Client - パフォーマンス", () => {
  test("レポート詳細の初期読み込み時間", async ({ page }) => {
    const startTime = Date.now();
    await page.goto("/test-report-1");
    await page.waitForLoadState("networkidle");
    // クラスタ情報が表示されるまでの時間を計測
    await expect(page.getByText(/生成AIと著作権に関する法的/).first()).toBeVisible();
    const loadTime = Date.now() - startTime;

    // 10秒以内に読み込まれることを確認
    expect(loadTime).toBeLessThan(10000);
  });
});

/**
 * 注意事項:
 * - このテストはダミーAPIサーバー（port 8002）を使用します
 * - テストフィクスチャは test/e2e/fixtures/client/ に配置
 * - ダミーAPIサーバーは playwright.config.ts の webServer で自動起動されます
 * - Next.jsのハイドレーション完了を待つため waitForLoadState("networkidle") が必須
 * - BirdXplorer fork では page.tsx で Header/Footer/Overview/BackButton/Reporter を
 *   コメントアウトしているため、それらの要素のテストは省略しています
 */
