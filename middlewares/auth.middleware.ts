import { Request, Response, NextFunction } from "express";
import jwt, { JwtPayload } from "jsonwebtoken";
import { User } from '../models/user.model';

export interface AuthRequest extends Request {
  user?: string | JwtPayload;
}

const authMiddleware = async (
  req: AuthRequest,
  res: Response,
  next: NextFunction
) => {
  try {
    const authHeader = req.headers["authorization"];
    if (!authHeader) {
      return res.status(401).json({ success: false, message: "Authorization header missing" });
    }

    const token = authHeader.split(" ")[1]; // Expect "Bearer <token>"
    if (!token) {
      return res.status(401).json({ success: false, message: "Token missing" });
    }

    const secret = process.env.SECRET_KEY as string;
    if (!secret) {
      console.error("SECRET_KEY is not defined or missing in the environment variables.");
      return res.status(500).json({ success: false, message: "Internal Server Error"});
    }

    const decoded = jwt.verify(token, secret);
    if (typeof decoded === 'object' && decoded !== null && 'id' in decoded) {
      const user = await User.findOne({ id: decoded.id });
      if (user) {
        req.user = decoded;
        next();
      } else {
        throw new Error('User not found in the decoded token');
      }
    }
    return res.status(401).json({ success: false, message: "Invalid Token" });
  } catch (error: any) {
    console.error(`Error in JWT Field, reason: ${error.message}`);
    return res.status(401).json({ success: false, message: "Unauthorized Request" });
  }
};


export default authMiddleware;