import { Document } from "mongoose";

// --------- USER DETAILS INTERFACE ------------
export interface IUserDetails {
    id: string;
    phonenumber: string;
}


// ----------- PREDICTION INTERFACE -----------
export interface IPrediciton extends Document {
    id: string;
    user: IUserDetails;

    predicted_disease: string;
    image_url: string;

    created_at: Date;
    updated_at: Date;
}