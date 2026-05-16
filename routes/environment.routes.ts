import express, { Response } from "express";
import authMiddleware, { AuthRequest } from "../middlewares/auth.middleware";
import { landData, todayWeather, Weather } from "../services/environment.service";

const router = express.Router();

// ----------------- WEATHER ROUTE ----------------------------
router.post('/weather', authMiddleware, async (req: AuthRequest, res: Response) => {
    if ( typeof req.user === 'object' && req.user !== null && 'id' in req.user) {
        let data: { lat: number, lon: number } = req.body;
        const result: { statusCode: number; success: boolean; message: string; details?:any } = await Weather(data);
        return res.status(result.statusCode).json({ success: result.success, message: result.message, ...(result.details && {details: result.details})});
    }
    return res.status(401).json({ message: "Invalid token payload" });
});


// ----------------- TODAY WEATHER ROUTE ----------------------------
router.post('/weather/today', authMiddleware, async (req: AuthRequest, res: Response) => {
    if ( typeof req.user === 'object' && req.user !== null && 'id' in req.user) {
        let data: { lat: number, lon: number } = req.body;
        const result: { statusCode: number; success: boolean; message: string; details?:any } = await todayWeather(data);
        return res.status(result.statusCode).json({ success: result.success, message: result.message, ...(result.details && {details: result.details})});
    }
    return res.status(401).json({ message: "Invalid token payload" });
});

// ----------------- LAND DETAILS ROUTE ----------------------------
router.post('/land-details', authMiddleware, async (req: AuthRequest, res: Response) => {
    if ( typeof req.user === 'object' && req.user !== null && 'id' in req.user) {
        let data: { lat: number, lon: number } = req.body;
        const result: { statusCode: number; success: boolean; message: string; details?:any } = await landData(data);
        return res.status(result.statusCode).json({ success: result.success, message: result.message, ...(result.details && {details: result.details})});
    }
    return res.status(401).json({ message: "Invalid token payload" });
});

export default router;