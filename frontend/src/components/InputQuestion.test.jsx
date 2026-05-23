import { act, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import InputQuestion from "./InputQuestion";

describe("InputQuestion", () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  test("sends message on button click and clears", async () => {
    const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });
    const onSend = jest.fn();

    render(<InputQuestion onSend={onSend} />);

    const textarea = screen.getByPlaceholderText("Type a question...");
    await act(async () => {
      await user.type(textarea, "Hello world");
    });

    const sendButton = screen.getByRole("button", { name: /send/i });
    await act(async () => {
      await user.click(sendButton);
    });

    await act(async () => {
      jest.runOnlyPendingTimers();
    });

    expect(onSend).toHaveBeenCalledWith("Hello world");
    expect(textarea).toHaveValue("");
  });

  test("sends message on Enter key", async () => {
    const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });
    const onSend = jest.fn();

    render(<InputQuestion onSend={onSend} />);

    const textarea = screen.getByPlaceholderText("Type a question...");
    await act(async () => {
      await user.type(textarea, "Ping{enter}");
    });

    await act(async () => {
      jest.runOnlyPendingTimers();
    });

    expect(onSend).toHaveBeenCalledWith("Ping");
  });

  test("does not send empty messages", async () => {
    const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });
    const onSend = jest.fn();

    render(<InputQuestion onSend={onSend} />);

    const textarea = screen.getByPlaceholderText("Type a question...");
    await act(async () => {
      await user.type(textarea, "   ");
    });

    const sendButton = screen.getByRole("button", { name: /send/i });
    await act(async () => {
      await user.click(sendButton);
    });

    await act(async () => {
      jest.runOnlyPendingTimers();
    });

    expect(onSend).not.toHaveBeenCalled();
  });
});
