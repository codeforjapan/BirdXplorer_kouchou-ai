import { test, expect } from "@playwright/test";

/**
 * Client Static - レポート詳細テスト（静的ビルド版）
 *
 * 静的ビルド（apps/public-viewer/out）をホスティングした環境での個別レポート詳細ページをテストします。
 * http://localhost:3001 で http-server により静的ファイルが提供されます。
 *
 * 注意:
 * - 静的ビルドは事前に生成されている必要があります（cd apps/public-viewer && pnpm run build:static）
 * - 静的HTMLなので、APIサーバーへのリクエストは発生しません
 * - ビルド時に埋め込まれたデータが表示されます
 * - BirdXplorer fork では Header/Footer/Overview/BackButton/Reporter を非表示にしているため、
 *   それらの要素に対するテストは含みません
 */

test.describe("Client Static - レポート詳細", () => {
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
    await expect(page.getByText(/404|Not Found|見つかりません/)).toBeVisible();
  });
});

test.describe("Client Static - レポート詳細のレスポンシブデザイン", () => {
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

test.describe("Client Static - パフォーマンス", () => {
  test("レポート詳細の初期読み込み時間", async ({ page }) => {
    const startTime = Date.now();
    await page.goto("/test-report-1");
    await page.waitForLoadState("networkidle");
    // クラスタ情報が表示されるまでの時間を計測
    await expect(page.getByText(/生成AIと著作権に関する法的/).first()).toBeVisible();
    const loadTime = Date.now() - startTime;

    // 静的HTMLは高速に読み込まれるはず（5秒以内）
    expect(loadTime).toBeLessThan(5000);
  });
});
