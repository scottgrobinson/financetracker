import { useSnackbarStore } from "@/stores/SnackbarStore";

export const doApiCall = async (
  url,
  method = "GET",
  expectingReturnData = true,
  postData = null,
  errorActionDescription = ""
) => {
  try {
    let response;
    if (postData) {
      response = await fetch(url, {
        method: method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(postData),
      });
    } else {
      response = await fetch(url, { method: method });
    }
    if (!response.ok) {
      throw new Error(`Expected HTTP 200, got HTTP ${response.status}`);
    }

    const json = await response.json();
    if (expectingReturnData) {
      return json;
    } else {
      if (!json.success) {
        throw new Error(
          json.error
            ? `Expected success response, but received error - ${json.error}`
            : `Expected success response, but success was not received`
        );
      }
      return json;
    }
  } catch (err) {
    const snackbarStore = useSnackbarStore();
    snackbarStore.openSnackbar(
      `Error ${errorActionDescription} - ${
        err.message || "An unknown error occurred"
      }`
    );
    throw err;
  }
};
