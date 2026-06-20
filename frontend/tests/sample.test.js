import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'

const DummyComponent = {
  template: '<div>Hello Vitest</div>'
}

describe('Sample Test', () => {
  it('renders correctly', () => {
    const wrapper = mount(DummyComponent)
    expect(wrapper.text()).toContain('Hello Vitest')
  })
})
