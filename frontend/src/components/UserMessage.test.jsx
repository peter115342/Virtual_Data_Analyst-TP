import { render, screen } from "@testing-library/react";
import UserMessage from "./UserMessage";

describe("UserMessage", () => {
  test("renders the message text", () => {
    render(<UserMessage context="Hello" isUser={true} />);

    expect(screen.getByText("Hello")).toBeInTheDocument();
  });

  test("renders a chart image when provided", () => {
    render(
      <UserMessage
        context="Chart"
        isUser={false}
        chartImage="/chart.png"
        chartTitle="Sales chart"
      />
    );

    expect(screen.getByRole("img", { name: "Sales chart" })).toBeInTheDocument();
  });
});
