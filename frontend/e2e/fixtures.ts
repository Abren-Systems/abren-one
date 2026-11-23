import { test as base, Page } from "@playwright/test";

export interface MockApiOptions {
  authenticated?: boolean;
  organizations?: Array<{
    organization_id: string;
    name: string;
    slug: string;
    role: "owner" | "admin" | "staff" | "member";
    status: "active" | "suspended" | "pending";
    is_active: boolean;
  }>;
}

export async function setupMockApi(page: Page, options: MockApiOptions = {}) {
  let isCurrentlyAuthenticated = options.authenticated !== undefined ? options.authenticated : true;
  const organizations = options.organizations || [
    {
      organization_id: "org-abren-test",
      name: "Abren Relief Initiative",
      slug: "abren-relief",
      role: "owner",
      status: "active",
      is_active: true,
    },
  ];

  // In-memory mock databases for the session
  const programs = [
    {
      id: "prog-1",
      organization_id: "org-abren-test",
      name: "Emergency Nutrition & Health",
      description: "Direct community supplementary nutrition support",
      start_date: "2026-01-01",
      end_date: "2026-12-31",
      is_active: true,
      status: "active",
    },
  ];

  const projects = [
    {
      id: "proj-1",
      organization_id: "org-abren-test",
      program_id: "prog-1",
      name: "Supplementary Feeding Clinic",
      description: "Mobile clinic stations",
      budget_currency: "USD",
      status: "active",
    },
  ];

  const activities = [
    {
      id: "act-1",
      organization_id: "org-abren-test",
      project_id: "proj-1",
      name: "Community Screenings",
      status: "in_progress",
      due_date: "2026-06-30",
    },
  ];

  const beneficiaries = [
    {
      id: "ben-1",
      organization_id: "org-abren-test",
      beneficiary_type: "individual",
      display_name: "Fatima Zahra",
      first_name: "Fatima",
      last_name: "Zahra",
      household_name: null,
      identification_number: "ID-90812",
      vulnerability_level: "high",
      status: "active",
    },
  ];

  const deliveries = [
    {
      id: "del-1",
      beneficiary_id: "ben-1",
      beneficiary_name: "Fatima Zahra",
      service_type: "food_ration",
      quantity: "25",
      unit: "kg",
      delivered_at: "2026-02-15T10:00:00Z",
      status: "delivered",
    },
  ];

  const donors = [
    {
      id: "donor-1",
      organization_id: "org-abren-test",
      name: "Global Food Assistance Fund",
      donor_type: "foundation",
      email: "grants@globalfood.org",
      phone: "+1-555-0182",
      status: "active",
      is_active: true,
    },
  ];

  const grants = [
    {
      id: "grant-1",
      organization_id: "org-abren-test",
      donor_id: "donor-1",
      donor_name: "Global Food Assistance Fund",
      title: "Nutrition Emergency Response",
      reference_code: "NER-2026",
      total_amount: "500000.00",
      currency: "USD",
      status: "active",
      is_active: true,
      start_date: "2026-01-01",
      end_date: "2026-12-31",
      program_id: "prog-1",
    },
  ];

  const donations = [
    {
      id: "don-1",
      organization_id: "org-abren-test",
      donor_id: "donor-1",
      donor_name: "Global Food Assistance Fund",
      grant_id: "grant-1",
      amount: "150000.00",
      currency: "USD",
      status: "confirmed",
      payment_method: "bank_transfer",
      reference: "WIRE-7782",
      received_at: "2026-01-20T12:00:00Z",
    },
  ];

  const accounts = [
    {
      id: "acc-1",
      code: "1010",
      name: "Cash and Bank Balances",
      account_type: "asset",
      is_active: true,
    },
    {
      id: "acc-2",
      code: "4010",
      name: "Grant Revenue",
      account_type: "revenue",
      is_active: true,
    },
  ];

  const journalEntries = [
    {
      id: "entry-1",
      entry_number: "JE-2026-0001",
      entry_date: "2026-01-15",
      memo: "Initial Grant Disbursement",
      status: "posted",
      lines: [
        { account_id: "acc-1", account_code: "1010", account_name: "Cash and Bank Balances", debit_amount: "50000.00", credit_amount: "0.00", description: "" },
        { account_id: "acc-2", account_code: "4010", account_name: "Grant Revenue", debit_amount: "0.00", credit_amount: "50000.00", description: "" },
      ],
    },
  ];

  const branches = [
    {
      id: "branch-1",
      organization_id: "org-abren-test",
      name: "Country Headquarters",
      code: "HQ",
      is_headquarters: true,
      is_active: true,
    },
  ];

  const departments = [
    {
      id: "dept-1",
      organization_id: "org-abren-test",
      branch_id: null,
      name: "Programs & Operations",
      code: "PROG",
      is_active: true,
    },
  ];

  const members = [
    {
      membership_id: "mem-1",
      user_id: "u1",
      username: "admin",
      email: "admin@abren.org",
      role: "owner",
      status: "active",
      is_active: true,
    },
  ];

  // Intercept and route all API calls
  await page.route("**/api/v1/**", async (route) => {
    const url = new URL(route.request().url());
    const path = url.pathname;
    const method = route.request().method();

    // CSRF
    if (path.includes("/auth/csrf/")) {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ csrfToken: "mock-csrf-token" }),
      });
    }

    // Auth me
    if (path.includes("/auth/me/")) {
      if (isCurrentlyAuthenticated) {
        return route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            id: "user-1",
            username: "admin",
            email: "admin@abren.org",
            first_name: "Yuma",
            last_name: "Admin",
            is_staff: true,
            is_superuser: false,
          }),
        });
      }
      return route.fulfill({
        status: 401,
        contentType: "application/json",
        body: JSON.stringify({ detail: "Authentication credentials were not provided." }),
      });
    }

    // Auth login
    if (path.includes("/auth/login/")) {
      const data = route.request().postDataJSON();
      if (data?.username && data?.password) {
        isCurrentlyAuthenticated = true;
        return route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            id: "user-1",
            username: data.username,
            email: `${data.username}@abren.org`,
            first_name: "Yuma",
            last_name: "Admin",
            is_staff: true,
            is_superuser: false,
          }),
        });
      }
      return route.fulfill({
        status: 400,
        contentType: "application/json",
        body: JSON.stringify({ detail: "Invalid credentials" }),
      });
    }

    // Auth logout
    if (path.includes("/auth/logout/")) {
      isCurrentlyAuthenticated = false;
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ detail: "Logged out" }),
      });
    }

    // Organizations list & create
    if (path === "/api/v1/organizations/" || path === "/api/v1/organizations") {
      if (method === "POST") {
        const body = route.request().postDataJSON();
        const newOrg = {
          organization_id: `org-${Date.now()}`,
          name: body.name,
          slug: body.slug,
          role: "owner" as const,
          status: "active" as const,
          is_active: true,
        };
        organizations.push(newOrg);
        return route.fulfill({
          status: 201,
          contentType: "application/json",
          body: JSON.stringify({ organization_id: newOrg.organization_id, slug: newOrg.slug }),
        });
      }
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(organizations),
      });
    }

    // Branches
    if (path.includes("/organizations/branches/")) {
      if (method === "POST") {
        const b = route.request().postDataJSON();
        const newBranch = {
          id: `branch-${Date.now()}`,
          organization_id: "org-abren-test",
          name: b.name,
          code: b.code,
          is_headquarters: false,
          is_active: true,
        };
        branches.push(newBranch);
        return route.fulfill({
          status: 201,
          contentType: "application/json",
          body: JSON.stringify({ branch_id: newBranch.id }),
        });
      }
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(branches),
      });
    }

    // Departments
    if (path.includes("/organizations/departments/")) {
      if (method === "POST") {
        const d = route.request().postDataJSON();
        const newDept = {
          id: `dept-${Date.now()}`,
          organization_id: "org-abren-test",
          branch_id: null,
          name: d.name,
          code: d.code,
          is_active: true,
        };
        departments.push(newDept);
        return route.fulfill({
          status: 201,
          contentType: "application/json",
          body: JSON.stringify({ department_id: newDept.id }),
        });
      }
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(departments),
      });
    }

    // Members
    if (path.includes("/organizations/members/")) {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(members),
      });
    }

    // Programs
    if (path === "/api/v1/programs/" || path === "/api/v1/programs") {
      if (method === "POST") {
        const p = route.request().postDataJSON();
        const newProg = {
          id: `prog-${Date.now()}`,
          organization_id: "org-abren-test",
          name: p.name,
          description: p.description || "",
          start_date: p.start_date || null,
          end_date: p.end_date || null,
          is_active: true,
          status: "active",
        };
        programs.push(newProg);
        return route.fulfill({
          status: 201,
          contentType: "application/json",
          body: JSON.stringify({ program_id: newProg.id }),
        });
      }
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(programs),
      });
    }

    // Projects
    if (path.includes("/programs/projects/")) {
      if (method === "POST") {
        const pr = route.request().postDataJSON();
        const newProject = {
          id: `proj-${Date.now()}`,
          organization_id: "org-abren-test",
          program_id: pr.program_id,
          name: pr.name,
          description: pr.description || "",
          budget_currency: pr.budget_currency || "USD",
          status: "active",
        };
        projects.push(newProject);
        return route.fulfill({
          status: 201,
          contentType: "application/json",
          body: JSON.stringify({ project_id: newProject.id }),
        });
      }
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(projects),
      });
    }

    // Activities
    if (path.includes("/programs/activities/")) {
      if (method === "POST") {
        const a = route.request().postDataJSON();
        const newAct = {
          id: `act-${Date.now()}`,
          organization_id: "org-abren-test",
          project_id: a.project_id,
          name: a.name,
          status: "planned",
          due_date: a.due_date || null,
        };
        activities.push(newAct);
        return route.fulfill({
          status: 201,
          contentType: "application/json",
          body: JSON.stringify({ activity_id: newAct.id }),
        });
      }
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(activities),
      });
    }

    // Beneficiaries
    if (path === "/api/v1/beneficiaries/" || path === "/api/v1/beneficiaries") {
      if (method === "POST") {
        const b = route.request().postDataJSON();
        const newBen = {
          id: `ben-${Date.now()}`,
          organization_id: "org-abren-test",
          beneficiary_type: b.beneficiary_type || "individual",
          display_name: b.household_name || `${b.first_name || ""} ${b.last_name || ""}`.trim() || "Beneficiary",
          first_name: b.first_name || null,
          last_name: b.last_name || null,
          household_name: b.household_name || null,
          identification_number: b.identification_number || `ID-${Date.now().toString().slice(-5)}`,
          vulnerability_level: b.vulnerability_level || "medium",
          status: "active",
        };
        beneficiaries.push(newBen);
        return route.fulfill({
          status: 201,
          contentType: "application/json",
          body: JSON.stringify({ beneficiary_id: newBen.id }),
        });
      }
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(beneficiaries),
      });
    }

    // Deliveries
    if (path.includes("/beneficiaries/deliveries/")) {
      if (method === "POST") {
        const d = route.request().postDataJSON();
        const newDelivery = {
          id: `del-${Date.now()}`,
          beneficiary_id: d.beneficiary_id,
          beneficiary_name: "Fatima Zahra",
          service_type: d.service_type,
          quantity: String(d.quantity),
          unit: d.unit,
          delivered_at: new Date().toISOString(),
          status: "delivered",
        };
        deliveries.push(newDelivery);
        return route.fulfill({
          status: 201,
          contentType: "application/json",
          body: JSON.stringify({ delivery_id: newDelivery.id }),
        });
      }
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(deliveries),
      });
    }

    // Donors
    if (path.includes("/fundraising/donors/")) {
      if (method === "POST") {
        const d = route.request().postDataJSON();
        const newDonor = {
          id: `donor-${Date.now()}`,
          organization_id: "org-abren-test",
          name: d.name,
          donor_type: d.donor_type,
          email: d.email || "",
          phone: d.phone || "",
          status: "active",
          is_active: true,
        };
        donors.push(newDonor);
        return route.fulfill({
          status: 201,
          contentType: "application/json",
          body: JSON.stringify({ donor_id: newDonor.id }),
        });
      }
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(donors),
      });
    }

    // Grants
    if (path.includes("/fundraising/grants/")) {
      if (method === "POST") {
        const g = route.request().postDataJSON();
        const newGrant = {
          id: `grant-${Date.now()}`,
          organization_id: "org-abren-test",
          donor_id: g.donor_id,
          donor_name: "Global Food Assistance Fund",
          title: g.title,
          reference_code: g.reference_code,
          total_amount: String(g.total_amount),
          currency: g.currency || "USD",
          status: "proposed",
          is_active: true,
          start_date: g.start_date,
          end_date: g.end_date,
          program_id: g.program_id || null,
        };
        grants.push(newGrant);
        return route.fulfill({
          status: 201,
          contentType: "application/json",
          body: JSON.stringify({ grant_id: newGrant.id }),
        });
      }
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(grants),
      });
    }

    // Donations
    if (path.includes("/fundraising/donations/")) {
      if (method === "POST") {
        const don = route.request().postDataJSON();
        const newDonation = {
          id: `don-${Date.now()}`,
          organization_id: "org-abren-test",
          donor_id: don.donor_id,
          donor_name: "Global Food Assistance Fund",
          grant_id: don.grant_id || null,
          amount: String(don.amount),
          currency: don.currency || "USD",
          status: "confirmed",
          payment_method: don.payment_method,
          reference: don.reference || "REF-AUTO",
          received_at: new Date().toISOString(),
        };
        donations.push(newDonation);
        return route.fulfill({
          status: 201,
          contentType: "application/json",
          body: JSON.stringify({ donation_id: newDonation.id }),
        });
      }
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(donations),
      });
    }

    // Finance Accounts
    if (path.includes("/finance/accounts/")) {
      if (method === "POST") {
        const a = route.request().postDataJSON();
        const newAcc = {
          id: `acc-${Date.now()}`,
          code: a.code,
          name: a.name,
          account_type: a.account_type,
          is_active: true,
        };
        accounts.push(newAcc);
        return route.fulfill({
          status: 201,
          contentType: "application/json",
          body: JSON.stringify({ account_id: newAcc.id }),
        });
      }
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(accounts),
      });
    }

    // Finance Journal Entries
    if (path.includes("/finance/journal-entries/")) {
      if (method === "POST") {
        const je = route.request().postDataJSON();
        const newEntry = {
          id: `entry-${Date.now()}`,
          entry_number: `JE-2026-${Date.now().toString().slice(-4)}`,
          entry_date: je.entry_date,
          memo: je.memo || je.description || "",
          status: "draft",
          lines: je.lines || [],
        };
        journalEntries.push(newEntry);
        return route.fulfill({
          status: 201,
          contentType: "application/json",
          body: JSON.stringify({ journal_entry_id: newEntry.id }),
        });
      }
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(journalEntries),
      });
    }

    // Finance Trial Balance
    if (path.includes("/finance/trial-balance/")) {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          as_of_date: "2026-11-23",
          currency: "USD",
          total_debits: "50000.00",
          total_credits: "50000.00",
          is_balanced: true,
          items: [
            { account_id: "acc-1", code: "1010", name: "Cash and Bank Balances", account_type: "asset", balance_debit: "50000.00", balance_credit: "0.00" },
            { account_id: "acc-2", code: "4010", name: "Grant Revenue", account_type: "revenue", balance_debit: "0.00", balance_credit: "50000.00" },
          ],
        }),
      });
    }

    // Procurement Requisitions & Vendors
    if (path.includes("/procurement/requisitions/")) {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([]),
      });
    }

    if (path.includes("/procurement/vendors/")) {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([]),
      });
    }

    // Inventory items & warehouses
    if (path.includes("/inventory/items/")) {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([]),
      });
    }

    if (path.includes("/inventory/warehouses/")) {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([]),
      });
    }

    // Default fallback for any other api
    return route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([]),
    });
  });
}

export const test = base.extend<{
  mockApi: void;
}>({
  mockApi: [
    async ({ page }, use) => {
      await setupMockApi(page);
      await use();
    },
    { auto: false },
  ],
});
