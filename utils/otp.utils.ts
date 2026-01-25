import { client } from "../config/twilio.config";

export const sendOTP = async (details: { phonenumber: string, otp: string }): Promise<{ success: boolean, message: string }> => {
    const { phonenumber, otp } = details;
    const recipientPhone: string = phonenumber.startsWith("+91") ? phonenumber : `+91${phonenumber}`;
    try {
        const testNumbers = [ "+917780706694", "+917842487664"];
        if (!testNumbers.includes(phonenumber)) {
            const message = await client.messages.create({
                body: `Your OTP for Verification in AgriVision application is ${otp}`,
                from: "MG75d173a98bb31033e1259b85884ad164",
                to: recipientPhone,
            });
            console.log(`OTP sent via SMS with SID: ${message.sid}`);
        }
        return { success: true, message: "Successfully sent the OTP using Twilio." };
    } catch (err: any) {
        console.error(`Error in sending the OTP using Twilio Service, reason: ${err.message}.`);
        return { success: false, message: "Issue in sending OTP using Twilio." };
    }
};