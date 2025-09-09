import { GraphQLClient } from "graphql-request";

const client = new GraphQLClient(
  "https://eu-graphql.contentstack.com/stacks/blt9d275b90d538983b?environment=development",
  {
    headers: {
      access_token: "cs400567746ad24e5df54591ba"
    }
  }
);

const query = `
query GetEntry($uid: String!, $locale: String!) {
  page(uid: $uid, locale: $locale) {
    title
    body
  }
}
`;

const variables = {
  uid: "blt7b8aea4e03d8ff75", // your entry UID
  locale: "en-us"
};

export default async function fetchEntry() {
  try {
    const data = await client.request(query, variables);
    console.log(data);
  } catch (err: any) {
    console.error("GraphQL fetch error:", err.response || err);
  }
}

fetchEntry();
