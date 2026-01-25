import express, { Request, Response } from "express";
import { login, resendOTP, verify } from '../services/auth.service';

const router = express.Router();

router.post('/login', async (req: Request, res: Response) => {
    const phonenumber: string = req.body.phonenumber;
    const result: { statusCode: number, success: boolean, message: string } = await login(phonenumber);
    return res.status(result.statusCode).json({ success: result.success, message: result.message });
});

router.post('/verify', async (req: Request, res: Response) => {
    const phonenumber: string = req.body.phonenumber;
    const otp: string = req.body.otp;
    const result: { statusCode: number, success: boolean, message: string, token?: string } = await verify({ phonenumber, otp });
    return res.status(result.statusCode).json({ success: result.success, message: result.message, ...(result.token && {token: result.token})});
});

router.post('/resend-otp', async (req: Request, res: Response) => {
    const phonenumber: string = req.body.phonenumber;
    const result: { statusCode: number, success: boolean, message: string } = await resendOTP(phonenumber);
    return res.status(result.statusCode).json({ success: result.success, message: result.message });
});

export default router;