import { Schema, model } from "mongoose";
import { v4 as uuidv4 } from "uuid";
import { IUser } from "../interfaces/models/user.interface";

// --------- USER SCHEMA -------------
const UserSchema = new Schema<IUser>({
    id: {
        type: String,
        default: () => uuidv4(),
        unique: true
    },
    phonenumber: {
        type: String,
        unique: true,
        required: true
    },
    otp: { type: String },
    otp_expires_at: { type: Date },
    history: [{
        id: { type: String, required: true },
        issue: { type: Date },
    }],
    created_at: { type: Date, default: Date.now },
    updated_at: { type: Date, default: Date.now } 
});

export const User = model<IUser>("User", UserSchema);