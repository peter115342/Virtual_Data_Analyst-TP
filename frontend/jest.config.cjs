module.exports = {
  roots: ["<rootDir>/src"],
  testEnvironment: "jsdom",
  setupFilesAfterEnv: ["<rootDir>/src/test/setupTests.cjs"],
  moduleNameMapper: {
    "\\.(css|less|scss|sass)$": "identity-obj-proxy",
    "\\.(gif|ttf|eot|svg|png|jpg|jpeg)$": "<rootDir>/src/test/fileMock.cjs",
  },
  transform: {
    "^.+\\.[jt]sx?$": "babel-jest",
  },
  testRegex: ".*\\.test\\.[jt]sx?$",
  clearMocks: true,
};
