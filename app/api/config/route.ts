import { NextRequest, NextResponse } from "next/server";
import { dbConnect } from "../../../lib/db";
import Config from "../../../models/Config";
import jwt from "jsonwebtoken";

export async function GET(req: NextRequest) {
  try {
    await dbConnect();
    
    console.log("GET /api/config - Connecting to database...");
    
    // Verify authentication
    const token = req.headers.get('authorization')?.replace('Bearer ', '');
    if (!token) {
      console.log("GET /api/config - No token provided");
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    // Verify token and get user ID
    let userId: string;
    try {
      const decoded = jwt.verify(token, process.env.JWT_SECRET as string) as any;
      userId = decoded.userId;
      console.log("GET /api/config - User ID:", userId);
    } catch (jwtError) {
      console.log("GET /api/config - Invalid token:", jwtError);
      return NextResponse.json({ error: "Invalid token" }, { status: 401 });
    }

    // Get user's config
    console.log("GET /api/config - Fetching config for user:", userId);
    const config = await Config.findOne({ userId });
    console.log("GET /api/config - Found config:", config ? "yes" : "no");

    if (!config) {
      return NextResponse.json({ config: null }, { status: 200 });
    }

    return NextResponse.json({ 
      config: {
        apiKey: config.apiKey, // Decrypted by post-find middleware
        environment: config.environment,
        accessToken: config.accessToken, // Decrypted by post-find middleware
        updatedAt: config.updatedAt
      }
    }, { status: 200 });

  } catch (error) {
    console.error("GET /api/config - Error:", error);
    return NextResponse.json({ error: "Server error" }, { status: 500 });
  }
}

export async function POST(req: NextRequest) {
  try {
    await dbConnect();
    console.log("POST /api/config - Connecting to database...");
    
    // Verify authentication
    const token = req.headers.get('authorization')?.replace('Bearer ', '');
    if (!token) {
      console.log("POST /api/config - No token provided");
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    // Verify token and get user ID
    let userId: string;
    try {
      const decoded = jwt.verify(token, process.env.JWT_SECRET as string) as any;
      userId = decoded.userId;
      console.log("POST /api/config - User ID:", userId);
    } catch (jwtError) {
      console.log("POST /api/config - Invalid token:", jwtError);
      return NextResponse.json({ error: "Invalid token" }, { status: 401 });
    }

    const { apiKey, environment, accessToken } = await req.json();
    console.log("POST /api/config - Received data:", { 
      apiKey: apiKey ? "present" : "missing", 
      environment, 
      accessToken: accessToken ? "present" : "missing" 
    });

    // Validate required fields
    if (!apiKey || !accessToken) {
      console.log("POST /api/config - Missing required fields");
      return NextResponse.json({ error: "API Key and Access Token are required" }, { status: 400 });
    }

    // Save or update user's configuration
    console.log("POST /api/config - Saving config for user:", userId);
    
    const config = await Config.findOneAndUpdate(
      { userId },
      {
        userId,
        apiKey, // Will be encrypted by pre-save middleware
        environment: environment || 'production',
        accessToken, // Will be encrypted by pre-save middleware
      },
      { 
        upsert: true, 
        new: true, 
        runValidators: true,
        setDefaultsOnInsert: true
      }
    );

    console.log("POST /api/config - Config saved successfully:", config ? "yes" : "no");

    if (!config) {
      throw new Error("Failed to save config");
    }

    return NextResponse.json({ 
      message: "Configuration saved successfully",
      config: {
        environment: config.environment,
        updatedAt: config.updatedAt
      }
    }, { status: 200 });

  } catch (error) {
    console.error("POST /api/config - Error:", error);
    return NextResponse.json({ error: "Server error" }, { status: 500 });
  }
}