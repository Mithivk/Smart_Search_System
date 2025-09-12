import { NextResponse } from "next/server";
import bcrypt from "bcryptjs";
import { dbConnect } from "../../../../lib/db";
import User from "../../../../models/Users";
import jwt from "jsonwebtoken";

export async function POST(req: Request) {
  try {
    await dbConnect();
    const { email, password } = await req.json();

    const user = await User.findOne({ email });
    if (!user) return NextResponse.json({ error: "Invalid credentials" }, { status: 401 });

    const isValid = await bcrypt.compare(password, user.password);
    if (!isValid) return NextResponse.json({ error: "Invalid credentials" }, { status: 401 });

const token = jwt.sign(
  { 
    userId: user._id.toString(), // Include user ID
    email: user.email 
  },
  process.env.JWT_SECRET as string,
  { expiresIn: "1d" }
);

    return NextResponse.json({ token }, { status: 200 });
  } catch (error) {
    return NextResponse.json({ error: "Server error" }, { status: 500 });
  }
}
