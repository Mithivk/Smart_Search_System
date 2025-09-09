const STACK_API_KEY = "blt9d275b90d538983b";
const DELIVERY_TOKEN = "cs400567746ad24e5df54591ba";
const CONTENT_TYPE = "page";

const url = `https://eu-cdn.contentstack.com/v3/content_types/${CONTENT_TYPE}/entries`;

async function fetchPageEntries() {
  try {
    const response = await fetch(url, {
      headers: {
        "api_key": STACK_API_KEY,
        "access_token": DELIVERY_TOKEN,
        "Content-Type": "application/json",
      },
    });
    const data = await response.json();
    console.log(data.entries);
  } catch (err) {
    console.error(err);
  }
}

fetchPageEntries();
