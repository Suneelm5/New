const express = require('express');
const crypto = require('crypto');
const Razorpay = require('razorpay');
require('dotenv').config();

const app = express();
const port = process.env.PORT || 3000;

app.use(express.json());

const razorpayKeyId = process.env.RAZORPAY_KEY_ID;
const razorpayKeySecret = process.env.RAZORPAY_KEY_SECRET;

let razorpay = null;
if (razorpayKeyId && razorpayKeySecret) {
  razorpay = new Razorpay({
    key_id: razorpayKeyId,
    key_secret: razorpayKeySecret,
  });
}

app.get('/health', (_req, res) => {
  res.json({ status: 'ok' });
});

app.get('/api/payment/config', (_req, res) => {
  if (!razorpayKeyId) {
    return res.status(500).json({
      error: 'Missing RAZORPAY_KEY_ID environment variable',
    });
  }

  return res.json({
    key: razorpayKeyId,
  });
});

app.post('/api/payment/create-order', async (req, res) => {
  try {
    if (!razorpay) {
      return res.status(500).json({
        error:
          'Razorpay is not configured. Add RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET to environment variables.',
      });
    }

    const { amount, currency = 'INR', receipt } = req.body;

    if (!amount || Number(amount) <= 0) {
      return res.status(400).json({
        error: 'amount is required and must be greater than 0',
      });
    }

    const order = await razorpay.orders.create({
      amount: Math.round(Number(amount) * 100),
      currency,
      receipt: receipt || `receipt_${Date.now()}`,
    });

    return res.json(order);
  } catch (error) {
    return res.status(500).json({
      error: 'Failed to create Razorpay order',
      details: error.message,
    });
  }
});

app.post('/api/payment/verify', (req, res) => {
  try {
    const {
      razorpay_order_id: orderId,
      razorpay_payment_id: paymentId,
      razorpay_signature: signature,
    } = req.body;

    if (!orderId || !paymentId || !signature) {
      return res.status(400).json({
        error:
          'razorpay_order_id, razorpay_payment_id, and razorpay_signature are required',
      });
    }

    if (!razorpayKeySecret) {
      return res.status(500).json({
        error: 'Missing RAZORPAY_KEY_SECRET environment variable',
      });
    }

    const expectedSignature = crypto
      .createHmac('sha256', razorpayKeySecret)
      .update(`${orderId}|${paymentId}`)
      .digest('hex');

    const isValid = expectedSignature === signature;

    return res.json({
      verified: isValid,
    });
  } catch (error) {
    return res.status(500).json({
      error: 'Failed to verify Razorpay payment',
      details: error.message,
    });
  }
});

app.listen(port, () => {
  console.log(`Payment API listening on port ${port}`);
});
