import { test, expect } from '@playwright/test';

test.describe('인증 및 UI 토글 플로우 E2E (TDD 스켈레톤)', () => {
  test('비로그인 시 로고와 로그인 버튼이 표시된다.', async ({ page }) => {
    // TODO: 팀원 기능 구현 후 테스트 활성화
    // await page.goto('/');
    // await expect(page.locator('.logo')).toBeVisible();
    // await expect(page.locator('text=로그인')).toBeVisible();
  });

  test('로그인 성공 후 로그인 버튼이 로그아웃으로 변경된다.', async ({ page }) => {
    // TODO: 기능 구현 후 테스트 로직 작성
  });
  
  test('회원정보 수정에서 비밀번호 보이기 버튼이 동작한다.', async ({ page }) => {
    // TODO: 기능 구현 후 테스트 로직 작성
  });
});
