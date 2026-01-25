import jwt from "jsonwebtoken";

// ------------ Generate Token for User ------------
const generateToken = async (id: string): Promise<
  | { success: true; token: string }
  | { success: false; message: string }
> => {
  const user = id;

  if (!process.env.SECRET_KEY) {
    return {
      success: false,
      message: "Error in generating the auth Token"
    };
  }

  const token = jwt.sign(
    { id: user },
    process.env.SECRET_KEY,
  );

  return {
    success: true,
    token: token
  };
};

export default generateToken;