import { dbConnect } from "./db";
import Config from "../models/Config";

export async function getUserConfig(userId: string) {
  try {
    await dbConnect();
    
    const config = await Config.findOne({ userId });
    
    if (!config) {
      return null;
    }

    // The getters in the schema automatically decrypt the values
    return {
      apiKey: config.apiKey, // Already decrypted
      accessToken: config.accessToken, // Already decrypted
      environment: config.environment,
      userId: config.userId
    };
  } catch (error) {
    console.error("Error fetching user config:", error);
    return null;
  }
}