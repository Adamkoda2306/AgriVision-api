import { Schema, model } from "mongoose";
import { v4 as uuidv4 } from "uuid";
import { IPrediciton } from "../interfaces/models/predicition.interface";

// -------------- PREDICTION SCHEMA -------------
const PredictionSchema = new Schema<IPrediciton>({
    id: {
        type: String,
        default: () => uuidv4(),
        unique: true,
    },
    user: {
        id: { type: String },
        phonenumber: { type: String },
    },

    predicted_disease: { type: String },
    image_url: { type: String }, 

    created_at: { type: Date, default: Date.now },
    updated_at: { type: Date, default: Date.now }
});

export const Prediction = model<IPrediciton>("Prediction", PredictionSchema);