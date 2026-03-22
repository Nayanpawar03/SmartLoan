const db = require('../config/db');
const { get } = require('../routes/authRoutes');

const upsertProfile = async (req, res) => {
    const user_id = req.user.id;

    const {
        age,
        monthly_income,
        existing_emi,
        loan_amount_requested,
        employment_type,
        credit_history_length,
        num_existing_loans,
        total_assets,
    } = req.body;

    try {
        const [existing] = await db.query(
            'SELECT id FROM user_financial_profiles WHERE user_id = ?',
            [user_id]
        );

        if (existing.length > 0) {
            await db.query(
                `UPDATE user_financial_profiles SET
                age = ?, monthly_income = ?, existing_emi = ?,
                loan_amount_requested = ?, num_existing_loans = ?,
                total_assets = ?
                WHERE user_id = ?`,
                [age, monthly_income, existing_emi, loan_amount_requested, employment_type, credit_history_length, num_existing_loans, total_assets, user_id]
            );
            return res.json({ message: 'Financial profile updated successfully' });
        }

        await db.query(
            `INSERT INTO user_financial_profiles
                (user_id, age, monthly_income, existing_emi, loan_amount_requested,
                employment_type, credit_history_length, num_existing_loans, total_assets)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
            [user_id, age, monthly_income, existing_emi, loan_amount_requested,
                employment_type, credit_history_length, num_existing_loans, total_assets]
        );

        res.status(201).json({ message: 'Financial profile created successfully' });
    } catch (err) {
        res.status(500).json({ message: 'Server error', error: err.message });
    }
};

const getProfile = async (req, res) => {
    const user_id = req.user.id;

    try {
        const [rows] = await db.query(
            'SELECT * FROM user_financial_profiles WHERE user_id = ?',
            [user_id]
        );

        if (rows.length === 0) {
            return res.status(404).json({ message: 'No financial profile found' });
        }

        res.json({ profile: rows[0] });
    } catch (err) {
        res.status(500).json({ message: 'Server error', error: err.message });
    }
};

module.exports = { upsertProfile, getProfile };