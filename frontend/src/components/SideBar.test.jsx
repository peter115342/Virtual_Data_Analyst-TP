import { render, screen } from "@testing-library/react";
import { listMongoSessions } from "../services/databaseService";
import SideBar from "./SideBar";

jest.mock("../services/databaseService", () => ({
  listMongoSessions: jest.fn(),
}));

describe("SideBar", () => {
  test("renders sessions from the API", async () => {
    listMongoSessions.mockResolvedValue({
      sessions: [
        {
          session_id: "abc",
          db_name: "Analytics DB",
          connected_at: "2024-01-01T10:00:00Z",
          messages: [{ role: "user", content: "Show sales metrics" }],
        },
      ],
    });

    const onSessionsFetched = jest.fn();

    render(
      <SideBar
        isOpenS={true}
        toggle={jest.fn()}
        isConnected={true}
        onSelectSession={jest.fn()}
        activeSessionId={null}
        onSessionsFetched={onSessionsFetched}
      />
    );

    expect(await screen.findByText("Analytics DB")).toBeInTheDocument();
    expect(screen.getByText("Show sales metrics...")).toBeInTheDocument();
    expect(onSessionsFetched).toHaveBeenCalledTimes(1);
  });

  test("renders an error when the API fails", async () => {
    listMongoSessions.mockRejectedValueOnce(new Error("fail"));

    render(
      <SideBar
        isOpenS={true}
        toggle={jest.fn()}
        isConnected={true}
        onSelectSession={jest.fn()}
        activeSessionId={null}
        onSessionsFetched={jest.fn()}
      />
    );

    expect(await screen.findByText("Failed to load sessions")).toBeInTheDocument();
  });
});
