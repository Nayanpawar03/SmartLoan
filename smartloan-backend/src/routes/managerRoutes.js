// src/routes/managerRoutes.js

const express = require('express');
const router = express.Router();
const {
    getAllUsers,
    getAllApplications,
    updateApplicationStatus,
    getRiskAnalytics
} = require('../controllers/managerController');
const { authenticate, authorizeManager } = require('../middleware/authMiddleware');

// All routes require valid JWT + manager role
router.use(authenticate, authorizeManager);

router.get('/users', getAllUsers);
router.get('/applications', getAllApplications);
router.patch('/applications/:id/status', updateApplicationStatus);
router.get('/analytics', getRiskAnalytics);

module.exports = router;
