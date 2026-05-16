import express, { Response } from "express";
import authMiddleware, { AuthRequest } from "../middlewares/auth.middleware";
import { getDiseaseInfo } from "../services/prediction.service";

const router = express.Router();

// ----------------- DISEASE INFO ROUTE ----------------------------
router.post('/disease-info', authMiddleware, async (req: AuthRequest, res: Response) => {
    if ( typeof req.user === 'object' && req.user !== null && 'id' in req.user) {
        let data: { disease: string } = req.body;
        let id = req.user.id as string;
        const result: { statusCode: number; success: boolean; message: string; description?: any } = await getDiseaseInfo({ id, disease: data.disease });
        return res.status(result.statusCode).json({ success: result.success, message: result.message, ...(result.description && {description: result.description})});
    }
    return res.status(401).json({ message: "Invalid token payload" });
});

export default router;