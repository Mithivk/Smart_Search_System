// app/page.tsx
import { GraphQLClient } from "graphql-request";

// Create GraphQL client
const client = new GraphQLClient(
  "https://eu-graphql.contentstack.com/stacks/blt9d275b90d538983b?environment=development",
  {
    headers: {
      access_token: "cs400567746ad24e5df54591ba",
    },
  }
);

// GraphQL query to fetch entry
const query = `
query GetEntry($uid: String!, $locale: String!) {
  page(uid: $uid, locale: $locale) {
    title
    body
  }
}
`;

const variables = {
  uid: "blt4c66bea4ba980144", // entry UID
  locale: "mr-in",
};

// Next.js page component
export default async function Home() {
  let data;
  try {
    const response = await client.request(query, variables);
    data = response.page;
  } catch (err: any) {
    console.error("GraphQL fetch error:", err.response || err);
    data = null;
  }

  if (!data) {
    return <main className="p-10">Entry not found or not published.</main>;
  }

  return (
    <main className="p-10">
      <h1 className="text-2xl font-bold">{data.title}</h1>
      <div>{data.body}</div>
    </main>
  );
}
