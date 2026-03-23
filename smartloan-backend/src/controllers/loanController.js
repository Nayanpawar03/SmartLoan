// src/controllers/loanController.js

const db = require('../config/db');
const { checkEligibility } = require('../utils/loanEligibility');

// GET loan recommendations based on latest assessment
const getLoanRecommendations = async (req, res) => {
    const user_id = req.user.id;

    try {
        const [assessments] = await db.query(
            'SELECT * FROM credit_assessments WHERE user_id = ? ORDER BY assessed_at DESC LIMIT 1',
            [user_id]
        );

        if (assessments.length === 0) {
            return res.status(404).json({ message: 'No credit assessment found. Please run an assessment first.' });
        }

        const [profiles] = await db.query(
            'SELECT * FROM user_financial_profiles WHERE user_id = ?',
            [user_id]
        );

        if (profiles.length === 0) {
            return res.status(404).json({ message: 'Financial profile not found.' });
        }

        const [loanProducts] = await db.query('SELECT * FROM loan_products');
        const result = checkEligibility(profiles[0], assessments[0], loanProducts);

        res.json({
            credit_score: assessments[0].fuzzy_credit_score,
            score_band: assessments[0].score_band,
            risk_level: assessments[0].risk_level,
            dti: result.dti,
            eligible_products: result.eligible,
            ineligible_products: result.ineligible
        });

    } catch (err) {
        res.status(500).json({ message: 'Server error', error: err.message });
    }
};

// POST apply for a loan
const applyForLoan = async (req, res) => {
    const user_id = req.user.id;
    const { loan_product_id, amount_requested } = req.body;

    try {
        // Get latest assessment
        const [assessments] = await db.query(
            'SELECT * FROM credit_assessments WHERE user_id = ? ORDER BY assessed_at DESC LIMIT 1',
            [user_id]
        );

        if (assessments.length === 0) {
            return res.status(400).json({ message: 'Please run a credit assessment before applying.' });
        }

        // Get financial profile
        const [profiles] = await db.query(
            'SELECT * FROM user_financial_profiles WHERE user_id = ?',
            [user_id]
        );

        if (profiles.length === 0) {
            return res.status(400).json({ message: 'Financial profile not found.' });
        }

        // Get the specific loan product
        const [products] = await db.query(
            'SELECT * FROM loan_products WHERE id = ?',
            [loan_product_id]
        );

        if (products.length === 0) {
            return res.status(404).json({ message: 'Loan product not found.' });
        }

        // Run eligibility check for this specific product
        const result = checkEligibility(profiles[0], assessments[0], products);

        if (result.eligible.length === 0) {
            return res.status(400).json({
                message: 'You are not eligible for this loan product.',
                reasons: result.ineligible[0]?.reasons || []
            });
        }

        const predicted_approval_amount = result.eligible[0].predicted_approval_amount;

        // Check for existing pending application for same product
        const [existing] = await db.query(
            'SELECT id FROM loan_applications WHERE user_id = ? AND loan_product_id = ? AND status = "pending"',
            [user_id, loan_product_id]
        );

        if (existing.length > 0) {
            return res.status(400).json({ message: 'You already have a pending application for this product.' });
        }

        // Insert application
        await db.query(
            `INSERT INTO loan_applications 
                (user_id, loan_product_id, amount_requested, predicted_approval_amount, status)
             VALUES (?, ?, ?, ?, 'pending')`,
            [user_id, loan_product_id, amount_requested, predicted_approval_amount]
        );

        res.status(201).json({
            message: 'Loan application submitted successfully',
            predicted_approval_amount,
            status: 'pending'
        });

    } catch (err) {
        res.status(500).json({ message: 'Server error', error: err.message });
    }
};

// GET all applications for logged-in user
const getMyApplications = async (req, res) => {
    const user_id = req.user.id;

    try {
        const [rows] = await db.query(
            `SELECT la.*, lp.name as product_name, lp.interest_rate, lp.tenure_months
             FROM loan_applications la
             JOIN loan_products lp ON la.loan_product_id = lp.id
             WHERE la.user_id = ?
             ORDER BY la.applied_at DESC`,
            [user_id]
        );

        res.json({ applications: rows });
    } catch (err) {
        res.status(500).json({ message: 'Server error', error: err.message });
    }
};

module.exports = { getLoanRecommendations, applyForLoan, getMyApplications };
