// src/controllers/managerController.js

const db = require('../config/db');

// GET all users
const getAllUsers = async (req, res) => {
    try {
        const [rows] = await db.query(
            `SELECT u.id, u.full_name, u.email, u.role, u.created_at,
                    ufp.monthly_income, ufp.employment_type,
                    ca.fuzzy_credit_score, ca.risk_level, ca.score_band
             FROM users u
             LEFT JOIN user_financial_profiles ufp ON u.id = ufp.user_id
             LEFT JOIN (
                SELECT user_id, fuzzy_credit_score, risk_level, score_band
                FROM credit_assessments
                WHERE id IN (
                    SELECT MAX(id) FROM credit_assessments GROUP BY user_id
                )
             ) ca ON u.id = ca.user_id
             WHERE u.role = 'user'
             ORDER BY u.created_at DESC`
        );

        res.json({ total: rows.length, users: rows });
    } catch (err) {
        res.status(500).json({ message: 'Server error', error: err.message });
    }
};

// GET all loan applications
const getAllApplications = async (req, res) => {
    try {
        const [rows] = await db.query(
            `SELECT la.id, la.status, la.amount_requested, la.predicted_approval_amount, la.applied_at,
                    u.full_name, u.email,
                    lp.name as product_name, lp.interest_rate, lp.tenure_months,
                    ca.fuzzy_credit_score, ca.risk_level, ca.score_band
             FROM loan_applications la
             JOIN users u ON la.user_id = u.id
             JOIN loan_products lp ON la.loan_product_id = lp.id
             LEFT JOIN (
                SELECT user_id, fuzzy_credit_score, risk_level, score_band
                FROM credit_assessments
                WHERE id IN (
                    SELECT MAX(id) FROM credit_assessments GROUP BY user_id
                )
             ) ca ON la.user_id = ca.user_id
             ORDER BY la.applied_at DESC`
        );

        res.json({ total: rows.length, applications: rows });
    } catch (err) {
        res.status(500).json({ message: 'Server error', error: err.message });
    }
};

// PATCH update application status (approve/reject)
const updateApplicationStatus = async (req, res) => {
    const { id } = req.params;
    const { status } = req.body;

    if (!['approved', 'rejected'].includes(status)) {
        return res.status(400).json({ message: 'Status must be "approved" or "rejected"' });
    }

    try {
        const [existing] = await db.query(
            'SELECT id FROM loan_applications WHERE id = ?', [id]
        );

        if (existing.length === 0) {
            return res.status(404).json({ message: 'Application not found' });
        }

        await db.query(
            'UPDATE loan_applications SET status = ? WHERE id = ?',
            [status, id]
        );

        res.json({ message: `Application ${status} successfully` });
    } catch (err) {
        res.status(500).json({ message: 'Server error', error: err.message });
    }
};

// GET risk analytics
const getRiskAnalytics = async (req, res) => {
    try {
        // Risk level distribution
        const [riskDist] = await db.query(
            `SELECT risk_level, COUNT(*) as count
             FROM (
                SELECT user_id, risk_level
                FROM credit_assessments
                WHERE id IN (
                    SELECT MAX(id) FROM credit_assessments GROUP BY user_id
                )
             ) latest
             GROUP BY risk_level`
        );

        // Average credit score
        const [avgScore] = await db.query(
            `SELECT ROUND(AVG(fuzzy_credit_score), 2) as avg_credit_score,
                    MIN(fuzzy_credit_score) as min_score,
                    MAX(fuzzy_credit_score) as max_score
             FROM (
                SELECT user_id, fuzzy_credit_score
                FROM credit_assessments
                WHERE id IN (
                    SELECT MAX(id) FROM credit_assessments GROUP BY user_id
                )
             ) latest`
        );

        // Application status breakdown
        const [appStats] = await db.query(
            `SELECT status, COUNT(*) as count,
                    ROUND(SUM(predicted_approval_amount), 2) as total_approval_amount
             FROM loan_applications
             GROUP BY status`
        );

        // Score band distribution
        const [scoreBands] = await db.query(
            `SELECT score_band, COUNT(*) as count
             FROM (
                SELECT user_id, score_band
                FROM credit_assessments
                WHERE id IN (
                    SELECT MAX(id) FROM credit_assessments GROUP BY user_id
                )
             ) latest
             GROUP BY score_band`
        );

        res.json({
            risk_distribution: riskDist,
            credit_score_stats: avgScore[0],
            application_stats: appStats,
            score_band_distribution: scoreBands
        });
    } catch (err) {
        res.status(500).json({ message: 'Server error', error: err.message });
    }
};

module.exports = { getAllUsers, getAllApplications, updateApplicationStatus, getRiskAnalytics };
