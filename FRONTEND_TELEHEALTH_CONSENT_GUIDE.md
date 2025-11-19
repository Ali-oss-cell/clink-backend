# 💻 Frontend Guide: Telehealth Consent & Emergency Workflow

This guide explains how to connect the new backend telehealth consent features to your React frontend.

---

## 1. API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/auth/telehealth-consent/` | Fetch patient’s telehealth consent details |
| POST | `/api/auth/telehealth-consent/` | Submit telehealth consent + emergency info |

---

## 2. Service Layer (`telehealthService.ts`)

```ts
import axiosInstance from './axiosInstance';

export const TelehealthService = {
  async getConsent() {
    const res = await axiosInstance.get('telehealth-consent/');
    return res.data;
  },

  async submitConsent(payload: {
    consent_to_telehealth: boolean;
    telehealth_emergency_protocol_acknowledged: boolean;
    telehealth_emergency_contact: string;
    telehealth_emergency_plan: string;
    telehealth_tech_requirements_acknowledged: boolean;
    telehealth_recording_consent?: boolean;
  }) {
    const res = await axiosInstance.post('telehealth-consent/', payload);
    return res.data;
  },
};
```

---

## 3. Consent Form Component

```tsx
function TelehealthConsentForm() {
  const [form, setForm] = useState({
    consent_to_telehealth: false,
    telehealth_emergency_protocol_acknowledged: false,
    telehealth_emergency_contact: '',
    telehealth_emergency_plan: '',
    telehealth_tech_requirements_acknowledged: false,
    telehealth_recording_consent: false,
  });

  const handleSubmit = async () => {
    await TelehealthService.submitConsent(form);
    alert('Telehealth consent saved!');
  };

  return (
    <form onSubmit={handleSubmit}>
      <label>
        <input
          type="checkbox"
          checked={form.consent_to_telehealth}
          onChange={e =>
            setForm({ ...form, consent_to_telehealth: e.target.checked })
          }
          required
        />
        I consent to telehealth sessions
      </label>

      <label>
        Emergency contact
        <input
          type="text"
          value={form.telehealth_emergency_contact}
          onChange={e =>
            setForm({ ...form, telehealth_emergency_contact: e.target.value })
          }
          placeholder="Name + phone"
          required
        />
      </label>

      <label>
        Emergency plan
        <textarea
          value={form.telehealth_emergency_plan}
          onChange={e =>
            setForm({ ...form, telehealth_emergency_plan: e.target.value })
          }
          placeholder="What should clinician do if connection drops / crisis occurs?"
          required
        />
      </label>

      <label>
        <input
          type="checkbox"
          checked={form.telehealth_emergency_protocol_acknowledged}
          onChange={e =>
            setForm({
              ...form,
              telehealth_emergency_protocol_acknowledged: e.target.checked,
            })
          }
          required
        />
        I understand the emergency procedures
      </label>

      <label>
        <input
          type="checkbox"
          checked={form.telehealth_tech_requirements_acknowledged}
          onChange={e =>
            setForm({
              ...form,
              telehealth_tech_requirements_acknowledged: e.target.checked,
            })
          }
          required
        />
        I meet the technical requirements (see{' '}
        <a href="https://yourclinic.com.au/telehealth-requirements" target="_blank">
          requirements
        </a>
        )
      </label>

      <label>
        <input
          type="checkbox"
          checked={form.telehealth_recording_consent}
          onChange={e =>
            setForm({
              ...form,
              telehealth_recording_consent: e.target.checked,
            })
          }
        />
        Allow session recording (optional)
      </label>

      <button type="submit">Save Telehealth Consent</button>
    </form>
  );
}
```

---

## 4. Displaying Consent Status

```tsx
function TelehealthConsentStatus() {
  const [data, setData] = useState<any>(null);
  useEffect(() => {
    TelehealthService.getConsent().then(setData);
  }, []);

  if (!data) return null;

  return (
    <section>
      <h3>Telehealth Consent</h3>
      <p>Status: {data.consent_to_telehealth ? '✅ Active' : '❌ Pending'}</p>
      <p>Version: {data.telehealth_consent_version || 'N/A'}</p>
      <p>Emergency contact: {data.telehealth_emergency_contact || 'Not set'}</p>
      <p>Recording consent: {data.telehealth_recording_consent ? 'Allowed' : 'Not allowed'}</p>
      <button onClick={/* open modal */}>Update Consent</button>
    </section>
  );
}
```

---

## 5. Intake Flow Integration
1. Add the telehealth consent section to your initial onboarding form.
2. Require patients to complete the telehealth consent before booking a telehealth appointment.
3. Display a warning banner in the dashboard if consent is missing.

---

## 6. Session Start Checks
Before starting a telehealth session:
- Fetch consent status.
- If recording is enabled for that appointment, verify `telehealth_recording_consent === true`. If not, prompt the clinician to disable recording or request consent.
- Show emergency contact and plan to the clinician in the session UI.

---

## 7. Links to Requirements Guide
Host the content from `TELEHEALTH_REQUIREMENTS.md` as a page and set `TELEHEALTH_REQUIREMENTS_URL` to that new URL so the backend response matches what you display.

---

## 8. Testing Checklist
- [ ] GET `/telehealth-consent/` works for logged-in patient
- [ ] POST `/telehealth-consent/` saves fields and returns success
- [ ] Consent status updates in UI
- [ ] Emergency contact visible to clinician before session
- [ ] Recording prompt respects patient consent

---

**Last Updated:** November 19, 2025

