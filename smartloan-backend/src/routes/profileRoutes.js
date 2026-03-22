const express = require('express');
const router = express.Router();
const { upsertProfile, getProfile } = require('../controllers/profileController');
const { authenticate } = require('../middleware/authMiddleware');

// All routes here require a valid JWT
router.post('/', authenticate, upsertProfile);
router.put('/', authenticate, upsertProfile);
router.get('/', authenticate, getProfile);

module.exports = router;
