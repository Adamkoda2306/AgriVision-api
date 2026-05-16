import { getLandData, getWeather, getWeatherToday } from "../utils/python.child.utils";


const Weather = async (details: { lat: number, lon: number }): Promise<
    { statusCode: number; success: boolean; message: string; details?:any }
> => {
    const { lat, lon } = details;
    try {
        if (!details) {
            return { statusCode: 400, success: false, message: "No Coordinates are Sent!!" };
        }
        const result: { success?: boolean; data?: any; error?: string } = await getWeather( lat, lon );
        if (!result.success) {
            return { statusCode: 400, success: false, message: "Failed to Get Weather for given Coordinates!" };
        } else {
            return { statusCode: 200, success: true, message: "Successfully got the Weather", details: result.data };
        }
    } catch (err: any) {
        console.error(`Error at Weather Service, reason: ${err.message}`);
        return { statusCode: 500, success: false, message: "Internal Server Issue" };
    }
};

const todayWeather = async (details: { lat: number, lon: number }): Promise<
    { statusCode: number; success: boolean; message: string; details?:any }
> => {
    const { lat, lon } = details;
    try {
        if (!details) {
            return { statusCode: 400, success: false, message: "No Coordinates are Sent!!" };
        }
        const result: { success?: boolean; data?: any; error?: string } = await getWeatherToday( lat, lon );
        if (!result.success) {
            return { statusCode: 400, success: false, message: "Failed to Get Weather for given Coordinates!" };
        } else {
            return { statusCode: 200, success: true, message: "Successfully got the Today's Weather", details: result.data };
        }
    } catch (err: any) {
        console.error(`Error at Today Weather Service, reason: ${err.message}`);
        return { statusCode: 500, success: false, message: "Internal Server Issue" };
    }
};

const landData = async (details: { lat: number, lon: number }): Promise<
    { statusCode: number; success: boolean; message: string; details?:any }
> => {
    const { lat, lon } = details;
    try {
        if (!details) {
            return { statusCode: 400, success: false, message: "No Coordinates are Sent!!" };
        }
        const result: { success?: boolean; data?: any; error?: string } = await getLandData( lat, lon );
        if (!result.success) {
            return { statusCode: 400, success: false, message: "Failed to Get Land Details for given Coordinates!" };
        } else {
            return { statusCode: 200, success: true, message: "Successfully got the Land Details", details: result.data };
        }
    } catch (err: any) {
        console.error(`Error at Land Data Service, reason: ${err.message}`);
        return { statusCode: 500, success: false, message: "Internal Server Issue" };
    }
};

export { Weather, todayWeather, landData };