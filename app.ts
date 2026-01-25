import express, { Response, Request, NextFunction } from "express";
import cors from 'cors';
import connectDB from './config/db.config';


// ----------------- ROUTES IMPORTS -----------------
import authRoutes from "./routes/auth.routes";
// import recommendRoutes from "./routes/recommend.routes";
// import predictionRoutes from "./routes/predict.routes";

const app = express();

// ----------------- MIDDLEWARE -----------------
app.use(cors({
  origin: true,
  credentials: true
}));

app.use(express.json());

app.use((req: Request, res: Response, next: NextFunction) => {
  console.log("➡️", req.method, req.url);
  console.log("IP:", req.ip);
  console.log("Headers:", req.headers['authorization']);
  console.log("Params:", req.params);
  console.log("Query:", req.query);
  console.log("Body:", req.body);
  next();
});


// ----------------- DATABASE CONNECTION -----------------
connectDB();

// ----------------- TEST ROUTES -----------------
app.get('/', (req: Request, res: Response) => {
    res.status(200).json({message: "Server Started!"});
});

app.get('/ping', (req: Request, res: Response) => {
    res.status(200).json({
        message: "OK",
        time: new Date().toString()
    });
});

// ----------------- ERROR HANDLER -----------------
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
    console.error(`Error: `, err.message);
    res.status(500).json({ error: "Internal Server Error!"});
});

// ----------------- ACTUAL ROUTES -----------------
app.use("/auth", authRoutes);
// app.use("/api/predict", predictionRoutes);
// app.use("/api/recommend", recommendRoutes);

export default app;