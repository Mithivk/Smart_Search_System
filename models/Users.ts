import mongoose, { Schema, Document } from "mongoose";

export interface IUser extends Document {
  email: string;
  password: string;
  credentials: {
    contentstackKey?: string;
    pineconeKey?: string;
  };
}

const UserSchema = new Schema<IUser>({
  email: { type: String, unique: true, required: true },
  password: { type: String, required: true },
  credentials: {
    contentstackKey: { type: String },
    contentstackEnviroment: { type: String },
  },
});

export default mongoose.models.User || mongoose.model<IUser>("User", UserSchema);
