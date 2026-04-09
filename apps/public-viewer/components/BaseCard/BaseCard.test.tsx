import { render, screen } from "@testing-library/react";
import { BaseCard } from "./BaseCard";

// Chakra UI の Provider をモック
jest.mock("@chakra-ui/react", () => {
  const actual = jest.requireActual("@chakra-ui/react");
  return {
    ...actual,
    Box: ({ children, ...props }: React.ComponentProps<"div">) => <div {...props}>{children}</div>,
    Flex: ({ children, ...props }: React.ComponentProps<"div">) => <div {...props}>{children}</div>,
  };
});

describe("BaseCard", () => {
  it("renders title and body correctly", () => {
    render(<BaseCard body={<div>Body Content</div>} title="Card Title" />);
    expect(screen.getByText("Card Title")).toBeInTheDocument();
    expect(screen.getByText("Body Content")).toBeInTheDocument();
  });

  it("renders complex ReactNode as title and body", () => {
    render(
      <BaseCard
        body={
          <div>
            <p>Paragraph 1</p>
            <p>Paragraph 2</p>
          </div>
        }
        title={
          <div>
            <span>Complex</span> <span>Title</span>
          </div>
        }
      />,
    );
    expect(screen.getByText("Complex")).toBeInTheDocument();
    expect(screen.getByText("Title")).toBeInTheDocument();
    expect(screen.getByText("Paragraph 1")).toBeInTheDocument();
    expect(screen.getByText("Paragraph 2")).toBeInTheDocument();
  });
});
