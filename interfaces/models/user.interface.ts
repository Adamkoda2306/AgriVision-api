import { Document } from "mongoose";

export interface IHistory {
    id: string;
    issue: Date;
}

export interface IUser extends Document {
    id: string;
    phonenumber: string;
    otp?: string;
    otp_expires_at?: Date;
    history: IHistory[];
    created_at: Date;
    updated_at: Date;
}