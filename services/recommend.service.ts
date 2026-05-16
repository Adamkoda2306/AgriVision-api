import { ICrop } from "../interfaces/services/recommend.interface";
import { getCropRecommendation, getFertilizerRecommendation } from "../utils/python.child.utils";


const getCrop = async (details: { data: ICrop }): Promise<
    { statusCode: number; success: boolean; message: string; details?:any }
> => {
    const { data } = details;
    try {
        if (!data) {
            return { statusCode: 400, success: false, message: "No Land Details are Sent!!" };
        }
        const result: { success?: boolean; data?: any; error?: string } = await getCropRecommendation( data.latitude, data.longitude, data.manual_data );
        console.log(result);
        if (!result.success) {
            return { statusCode: 400, success: false, message: "Failed to Get Recommended Crop!" };
        } else {
            return { statusCode: 200, success: true, message: "Successfully got the Recommended Crops", details: result.data };
        }
    } catch (err: any) {
        console.error(`Error at Crop Recommendation Service, reason: `, err);
        return { statusCode: 500, success: false, message: "Internal Server Issue" };
    }
};

const getFertilizer = async (details: { lat: number, lon: number, crop: string }): Promise<
    { statusCode: number; success: boolean; message: string; details?:any }
> => {
    const { lat, lon, crop } = details;
    try {
        if (!details) {
            return { statusCode: 400, success: false, message: "No Details are Sent!!" };
        }
        const result: { success?: boolean; data?: any; error?: string } = await getFertilizerRecommendation( lat, lon, crop );
        if (!result.success) {
            return { statusCode: 400, success: false, message: "Failed to Get Recommended Fertilizer for the Crop!" };
        } else {
            return { statusCode: 200, success: true, message: "Successfully got the Recommended Fertilizer for the Crop", details: result.data };
        }
    } catch (err: any) {
        console.error(`Error at Fertilizer Recommendation Service, reason: `, err);
        return { statusCode: 500, success: false, message: "Internal Server Issue" };
    }
};

export { getCrop, getFertilizer };