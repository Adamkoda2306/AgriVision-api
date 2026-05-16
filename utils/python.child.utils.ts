import { spawn, ChildProcess } from "child_process";
import path from "path";
import { fileURLToPath } from "url";

/**
 * Interface for request parameters
 */
interface RequestParams {
  lat?: number;
  lon?: number;
  manual_data?: Record<string, any>;
  crop_disease?: string;
  [key: string]: any;
}

/**
 * Interface for the response
 */
interface PredictionResult {
  success?: boolean;
  data?: any;
  error?: string;
}

/**
 * Get __dirname equivalent in ES modules
 * If using CommonJS, you can use __dirname directly
 */

const getDir = (): string => {
    return __dirname;
};

/**
 * Run AgriVision predictions using Python child process
 * @param requestType - Type of prediction (crop, weather, fertilizer, soil_moisture, weather_alerts, disease)
 * @param params - Parameters for the prediction
 * @returns Promise resolving to prediction result
 */
export const runAgriVisionPrediction = (
  requestType: string,
  params: RequestParams
): Promise<PredictionResult> => {
  const baseDir = getDir();
  const scriptPath = path.resolve(
    baseDir,
    "../python-services/AgriVision/usage.py"
  );

  return new Promise((resolve, reject) => {
    const pythonProcess: ChildProcess = spawn("python3", [
      scriptPath,
      requestType,
      JSON.stringify(params),
    ]);

    let output = "";
    let errorOutput = "";

    pythonProcess.stdout?.on("data", (data: Buffer) => {
      output += data.toString();
    });

    pythonProcess.stderr?.on("data", (data: Buffer) => {
      errorOutput += data.toString();
    });

    pythonProcess.on("close", (code: number | null) => {
      if (code === 0) {
        try {
          const result: PredictionResult = JSON.parse(output);
          resolve(result);
        } catch (err) {
          reject(`Failed to parse Python output: ${String(err)}`);
        }
      } else {
        reject(
          `Python exited with code ${code}. Error: ${errorOutput || output}`
        );
      }
    });

    pythonProcess.on("error", (err: Error) => {
      reject(`Failed to start Python process: ${err.message}`);
    });
  });
};

/**
 * Convenience function for crop recommendation
 */
export const getCropRecommendation = (
  lat: number,
  lon: number,
  manual_data: Record<string, any>
): Promise<PredictionResult> => {
  return runAgriVisionPrediction("crop", {
    lat,
    lon,
    manual_data
  });
};

/**
 * Convenience function for weather forecast
 */
export const getWeather = (
  lat: number,
  lon: number
): Promise<PredictionResult> => {
  return runAgriVisionPrediction("weather", { lat, lon });
};

/**
 * Convenience function for fertilizer recommendation
 */
export const getFertilizerRecommendation = (
  lat: number,
  lon: number,
  crop: string
): Promise<PredictionResult> => {
  return runAgriVisionPrediction("fertilizer", {
    lat,
    lon,
    crop
  });
};

/**
 * Convenience function for soil moisture
 */
export const getLandData = (
  lat: number,
  lon: number
): Promise<PredictionResult> => {
  return runAgriVisionPrediction("manual_data", { lat, lon });
};

/**
 * Convenience function for weather alerts
 */
export const getWeatherToday = (
  lat: number,
  lon: number
): Promise<PredictionResult> => {
  return runAgriVisionPrediction("weather_today", { lat, lon });
};

/**
 * Convenience function for disease prediction
 */
export const getDiseasePrediction = (
  cropDisease: string
): Promise<PredictionResult> => {
  return runAgriVisionPrediction("disease", { crop_disease: cropDisease });
};