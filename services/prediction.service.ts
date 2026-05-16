import { IPrediciton } from "../interfaces/models/predicition.interface";
import { Prediction } from "../models/prediction.model";
import { User } from "../models/user.model";
import { getDiseasePrediction } from "../utils/python.child.utils";


const getDiseaseInfo = async (details: { id: string, disease: string }): Promise<
    { statusCode: number; success: boolean; message: string; description?: any }
> => {
    const { id, disease } = details;
    try {
        if (!disease) {
            return { statusCode: 400, success: false, message: "No Disease Name is Sent!!" };
        }
        const userMain = await User.findOne({ id: id });
        if (!userMain) {
            return { statusCode: 400, success: false, message: "User not Found!!" };
        }
        const result: { success?: boolean; data?: any; error?: string } = await getDiseasePrediction(disease);
        if (!result.success) {
            return { statusCode: 400, success: false, message: "Failed to Get Disease Info!" };
        } else {
            const data: Partial<IPrediciton> = {
                user: {
                    id: id,
                    phonenumber: userMain.phonenumber
                },
                predicted_disease: disease
            };
            const predictionData = await Prediction.create(data);
            const historyUpdate: { id: string, issue: Date } = {
                id: predictionData.id,
                issue: predictionData.created_at
            };
            userMain.history.push(historyUpdate);
            await userMain.save();
            return { statusCode: 200, success: true, message: "Successfully got the Description", description: result.data };
        }
    } catch (err: any) {
        console.error(`Error at Prediction Service, reason: `, err);
        return { statusCode: 500, success: false, message: "Internal Server Issue" };
    }
};

export { getDiseaseInfo };