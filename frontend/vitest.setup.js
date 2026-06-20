import { beforeAll, afterEach, afterAll } from 'vitest'
import { server } from './src/mocks/server'
import { config } from '@vue/test-utils'

// MSW Server Setup
beforeAll(() => server.listen({ onUnhandledRequest: 'error' }))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

// 전역 목업 또는 플러그인 설정
config.global.mocks = {
  $route: {},
  $router: {
    push: vi.fn(),
    replace: vi.fn(),
  }
}
