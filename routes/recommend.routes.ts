import express, { Response } from "express";
import authMiddleware, { AuthRequest } from "../middlewares/auth.middleware";
import { ICrop } from "../interfaces/services/recommend.interface";
import { getCrop, getFertilizer } from "../services/recommend.service";

const router = express.Router();

// ----------------- CROP RECOMMENDATION ROUTE ----------------------------
router.post('/crop', authMiddleware, async (req: AuthRequest, res: Response) => {
    if ( typeof req.user === 'object' && req.user !== null && 'id' in req.user) {
        let data: { details: ICrop } = req.body;
        const result: { statusCode: number; success: boolean; message: string; details?:any } = await getCrop({ data: data.details });
        return res.status(result.statusCode).json({ success: result.success, message: result.message, ...(result.details && {details: result.details})});
    }
    return res.status(401).json({ message: "Invalid token payload" });
});

// ----------------- FERTILIZER RECOMMENDATION ROUTE ----------------------------
router.post('/fertilizer', authMiddleware, async (req: AuthRequest, res: Response) => {
    if ( typeof req.user === 'object' && req.user !== null && 'id' in req.user) {
        let data: { lat: number, lon: number, crop: string } = req.body;
        const result: { statusCode: number; success: boolean; message: string; details?:any } = await getFertilizer(data);
        return res.status(result.statusCode).json({ success: result.success, message: result.message, ...(result.details && {details: result.details})});
    }
    return res.status(401).json({ message: "Invalid token payload" });
});

export default router;