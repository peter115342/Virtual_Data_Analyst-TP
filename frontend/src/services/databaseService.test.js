import api from "./api";
import {
    connectDatabase,
    disconnectDatabase,
    listMongoSessions,
} from "./databaseService";

jest.mock("./api", () => ({
  __esModule: true,
  default: {
    post: jest.fn(),
    get: jest.fn(),
  },
}));

describe("databaseService", () => {
  test("connectDatabase posts data and returns payload", async () => {
    api.post.mockResolvedValue({ data: { ok: true } });

    const result = await connectDatabase({ db_type: "postgres" });

    expect(api.post).toHaveBeenCalledWith("/api/connect-database", { db_type: "postgres" });
    expect(result).toEqual({ ok: true });
  });

  test("disconnectDatabase posts with session id", async () => {
    api.post.mockResolvedValue({ data: { ok: true } });

    await disconnectDatabase(null);

    expect(api.post).toHaveBeenCalledWith("/api/disconnect-database", {
      session_id: null,
    });
  });

  test("listMongoSessions throws when no data is returned", async () => {
    api.get.mockResolvedValue({ data: null });

    await expect(listMongoSessions()).rejects.toThrow("No data returned");
  });
});
