import crypto from "crypto";
import { IUser } from '../interfaces/models/user.interface';
import { User } from '../models/user.model';
import { sendOTP } from "../utils/otp.utils";
import generateToken from "../utils/jwt.utils";

const login = async (phonenumber: string): Promise<{statusCode: number, success: boolean, message: string}> => {
    try {
        let otp: string;
        const testNumbers = [ "7780706694", "7842487664" ];
        otp = testNumbers.includes(phonenumber) ? "12345" : (crypto.randomInt(10000, 99999)).toString();
        const expiry: Date = new Date(Date.now() + 3 * 60 * 1000);
        const user = await User.findOneAndUpdate(
            { phonenumber: phonenumber},
            { $set: { otp: otp, otp_expires_at: expiry}},
            { new: true }
        );
        if (!user) {
            const userData: Partial<IUser> = {
                phonenumber: phonenumber,
                otp: otp,
                otp_expires_at: expiry,
                history: []
            };
            try {
                await User.create(userData);
                const result: { success: boolean, message: string } = await sendOTP({ phonenumber, otp});
                if (result.success) {
                    return { statusCode: 201, success: true, message: "Successfully Created account, OTP is sent to the registered mobile number."};
                } else {
                    throw new Error('Twilio Service unable to send the OTP.');
                }
            } catch (err: any) {
                if (err.code === 11000) {
                    // Try the update one last time since we now know the record exists
                    await User.updateOne({ phonenumber }, { $set: { otp: otp, otp_expires_at: expiry } });
                    const result: { success: boolean, message: string } = await sendOTP({ phonenumber, otp});
                    if (result.success) {
                        return { statusCode: 200, success: true, message: "OTP sent to registered number." };
                    } else {
                        throw new Error('Twilio Service unable to send the OTP.');
                    }   
                }
                throw err;
            }
        }
        const result: { success: boolean, message: string } = await sendOTP({ phonenumber, otp});
        if (result.success) {
            return { statusCode: 200, success: true, message: "Successfully sent OTP to the registered mobile number." };
        } else {
            throw new Error('Twilio Service unable to send the OTP.');
        }
    } catch (err: any) {
        console.error(`Error at Login Service, reason: ${err.message}`);
        return { statusCode: 500, success: false, message: "Internal Server Error" };
    }
};


const verify = async (details: { phonenumber: string, otp: string }): Promise<{ statusCode: number, success: boolean, message: string, token?: string}> => {
    const { phonenumber, otp } = details;
    try {
        const user = await User.findOne({ phonenumber: phonenumber });
        if (!user) {
            return { statusCode: 404, success: false, message: "User not Found!"};
        }
        if (user.otp_expires_at) {
            if ( user.otp === otp && user.otp_expires_at > new Date()) {
                const usertoken: { success: true; token: string }
                    | { success: false; message: string } = await generateToken(user.id);
                if (usertoken.success) {
                    return { statusCode: 200, success: true, message: "Successfully Verified!", token: usertoken.token };
                } else {
                    throw new Error('Failed to Generate the JWT Token for the User');
                }
            }
        }
        return { statusCode: 400, success: false, message: "Invalid OTP, Try again!" };
    } catch (err: any) {
        console.error(`Error at Verify Service, reason: ${err.message}`);
        return { statusCode: 500, success: false, message: "Internal Server Error" };
    }
};


const resendOTP = async (phonenumber: string): Promise<{ statusCode: number, success: boolean, message: string}> => {
    try {
        const testNumbers = ["7780706694", "7842487664"];
        let otp: string = testNumbers.includes(phonenumber) ? "12345" : (crypto.randomInt(10000, 99999)).toString();
        const expiry = new Date(Date.now() + 3 * 60 * 1000);
        const user = await User.findOneAndUpdate(
            { phonenumber: phonenumber },
            { $set: { otp: otp, otp_expires_at: expiry}},
            { new: true }
        );
        if (user) {
            const result: { success: boolean, message: string } = await sendOTP({ phonenumber, otp});
            if (result.success) {
                return { statusCode: 200, success: true, message: "Successfully resend OTP to the registered mobile number." };
            } else {
                throw new Error('Twilio Service unable to send the OTP.');
            }
        }
        return { statusCode: 404, success: false, message: "User not Found!"};
    } catch (err: any) {
        console.error(`Error at Resend OTP Service, reason: ${err.message}`);
        return { statusCode: 500, success: false, message: "Internal Server Error" };
    }
};


export { login, verify, resendOTP };