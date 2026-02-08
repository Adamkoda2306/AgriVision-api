import { IPrediciton } from "../interfaces/models/predicition.interface";
import { Prediction } from "../models/prediction.model";
import { User } from "../models/user.model";


const Predict = async (details: { id: string, image: File }): Promise<
    { statusCode: number; success: boolean; message: string; disease?: string }
> => {
    const { id, image } = details;
    try {

        return { statusCode: 400, success: false, message: "Failed to Predict" };
    } catch (err: any) {
        console.error(``);
        return { statusCode: 500, success: false, message: "Internal Server Issue" };
    }
};

export { Predict };