import { act, renderHook } from "@testing-library/react";
import { connectDatabase, disconnectDatabase } from "../services/databaseService";
import useDatabase from "./useDatabase";

jest.mock("../services/databaseService", () => ({
  connectDatabase: jest.fn(),
  disconnectDatabase: jest.fn(),
}));

describe("useDatabase", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  test("connect stores the session id", async () => {
    connectDatabase.mockResolvedValue({ session_id: "session-123" });

    const { result } = renderHook(() => useDatabase());

    await act(async () => {
      await result.current.connect({ db_type: "postgres" });
    });

    expect(connectDatabase).toHaveBeenCalledWith({ db_type: "postgres" });
    expect(result.current.sessionId).toBe("session-123");
    expect(localStorage.getItem("active_session_id")).toBe("session-123");
    expect(result.current.loading).toBe(false);
  });

  test("connect stores the error message on failure", async () => {
    connectDatabase.mockRejectedValue({
      response: { data: { detail: "Connection rejected" } },
    });

    const { result } = renderHook(() => useDatabase());

    await act(async () => {
      await expect(result.current.connect({})).rejects.toBeDefined();
    });

    expect(result.current.error).toBe("Connection rejected");
    expect(result.current.loading).toBe(false);
  });

  test("disconnect clears the session id", async () => {
    localStorage.setItem("active_session_id", "session-abc");
    disconnectDatabase.mockResolvedValue({ ok: true });

    const { result } = renderHook(() => useDatabase());

    await act(async () => {
      await result.current.disconnect();
    });

    expect(disconnectDatabase).toHaveBeenCalledWith("session-abc");
    expect(result.current.sessionId).toBe(null);
    expect(localStorage.getItem("active_session_id")).toBe(null);
  });
});
