import twilio from 'twilio';

export const client = twilio(process.env.TWILIO_ACCOUNT_SSID, process.env.TWILIO_AUTH_TOKEN);