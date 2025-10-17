import { render, screen } from "@testing-library/react"
import { describe, it, expect } from "vitest"

describe("Example Test", () => {
  it("should render", () => {
    render(<div>Hello World</div>)
    expect(screen.getByText("Hello World")).toBeInTheDocument()
  })
})

