# Upgrade Changes Log — run_006

## Metadata
- **Run:** run_006
- **Date:** Fri Apr 17 02:01:43 WIB 2026
- **Dump:** /Users/tri-mac/project/porting-0415-3/arkanadigital-roedl-main-6002510_2026-04-15_110617_test_fs.zip
- **Target:** Odoo 19.0
- **Status:** FAILED — errors detected

## Error Summary
```
FileNotFoundError: [Errno 2] No such file or directory: '/home/odoo/.local/share/Odoo/filestore/db_4193076/d5/d5cce68bf4bb4ab57beaf766f3fb775cf8df0c83'
FileNotFoundError: [Errno 2] No such file or directory: '/home/odoo/.local/share/Odoo/filestore/db_4193076/d5/d5cce68bf4bb4ab57beaf766f3fb775cf8df0c83'
FileNotFoundError: [Errno 2] No such file or directory: '/home/odoo/.local/share/Odoo/filestore/db_4193076/d5/d5cce68bf4bb4ab57beaf766f3fb775cf8df0c83'
FileNotFoundError: [Errno 2] No such file or directory: '/home/odoo/.local/share/Odoo/filestore/db_4193076/d5/d5cce68bf4bb4ab57beaf766f3fb775cf8df0c83'
FileNotFoundError: [Errno 2] No such file or directory: '/home/odoo/.local/share/Odoo/filestore/db_4193076/d5/d5cce68bf4bb4ab57beaf766f3fb775cf8df0c83'
FileNotFoundError: [Errno 2] No such file or directory: '/home/odoo/.local/share/Odoo/filestore/db_4193076/bc/bcb0b0aad1fc08833cb14c6a23dee942a17e1f53'
FileNotFoundError: [Errno 2] No such file or directory: '/home/odoo/.local/share/Odoo/filestore/db_4193076/bc/bcb0b0aad1fc08833cb14c6a23dee942a17e1f53'
FileNotFoundError: [Errno 2] No such file or directory: '/home/odoo/.local/share/Odoo/filestore/db_4193076/bc/bcb0b0aad1fc08833cb14c6a23dee942a17e1f53'
FileNotFoundError: [Errno 2] No such file or directory: '/home/odoo/.local/share/Odoo/filestore/db_4193076/bc/bcb0b0aad1fc08833cb14c6a23dee942a17e1f53'
ValueError: Element '<xpath expr="//div[hasclass(&#39;settings&#39;)]/div[@data-key=&#39;account&#39;]">' cannot be located in parent view
ValueError: Element '<xpath expr="//div[hasclass(&#39;settings&#39;)]/div[@data-key=&#39;account&#39;]">' cannot be located in parent view
ValueError: Element '<xpath expr="//div[hasclass(&#39;settings&#39;)]/div[@data-key=&#39;account&#39;]">' cannot be located in parent view
ValueError: Element '<xpath expr="//div[hasclass(&#39;settings&#39;)]/div[@data-key=&#39;account&#39;]">' cannot be located in parent view
ValueError: Element '<xpath expr="//div[hasclass(&#39;settings&#39;)]/div[@data-key=&#39;account&#39;]">' cannot be located in parent view
ValueError: Element '<xpath expr="//div[hasclass(&#39;settings&#39;)]/div[@data-key=&#39;account&#39;]">' cannot be located in parent view
ValueError: Element '<xpath expr="//div[hasclass(&#39;settings&#39;)]/div[@data-key=&#39;account&#39;]">' cannot be located in parent view
ValueError: Element '<xpath expr="//div[hasclass(&#39;settings&#39;)]/div[@data-key=&#39;account&#39;]">' cannot be located in parent view
ValueError: Element '<xpath expr="//div[hasclass(&#39;settings&#39;)]/div[@data-key=&#39;account&#39;]">' cannot be located in parent view
ValueError: Element '<xpath expr="//div[hasclass(&#39;settings&#39;)]/div[@data-key=&#39;account&#39;]">' cannot be located in parent view
ValueError: Element '<xpath expr="//div[hasclass(&#39;settings&#39;)]/div[@data-key=&#39;account&#39;]">' cannot be located in parent view
ValueError: Element '<xpath expr="//div[hasclass(&#39;settings&#39;)]/div[@data-key=&#39;account&#39;]">' cannot be located in parent view
ValueError: Element '<xpath expr="//div[hasclass(&#39;settings&#39;)]/div[@data-key=&#39;account&#39;]">' cannot be located in parent view
ValueError: Element '<xpath expr="//div[hasclass(&#39;settings&#39;)]/div[@data-key=&#39;account&#39;]">' cannot be located in parent view
ValueError: Element '<xpath expr="//div[hasclass(&#39;settings&#39;)]/div[@data-key=&#39;account&#39;]">' cannot be located in parent view
ValueError: Element '<xpath expr="//div[hasclass(&#39;settings&#39;)]/div[@data-key=&#39;account&#39;]">' cannot be located in parent view
ValueError: Element '<xpath expr="//button[@name=&#39;action_assign_to_me&#39;]">' cannot be located in parent view
ValueError: Element '<xpath expr="//button[@name=&#39;action_assign_to_me&#39;]">' cannot be located in parent view
ValueError: Element '<xpath expr="//button[@name=&#39;action_assign_to_me&#39;]">' cannot be located in parent view
ValueError: Element '<xpath expr="//button[@name=&#39;action_assign_to_me&#39;]">' cannot be located in parent view
ValueError: Element '<xpath expr="//button[@name=&#39;action_assign_to_me&#39;]">' cannot be located in parent view
ValueError: Element '<xpath expr="//field[@name=&#39;deposit_taxes_id&#39;]">' cannot be located in parent view
KeyError: ('ir.model.data', <function IrModelData._xmlid_lookup at 0x7786dd47b2e0>, 'account.1_l10n_id_21221020')
ValueError: External ID not found in the system: account.1_l10n_id_21221020
KeyError: ('ir.model.data', <function IrModelData._xmlid_lookup at 0x7786dd47b2e0>, 'account.1_l10n_id_21221020')
ValueError: External ID not found in the system: account.1_l10n_id_21221020
2026-04-17 02:01:42 ERROR: The upgrade request has failed
```

## Categories Detected

## Files Generated
- Log: /Users/tri-mac/.claude/skills/odoo-db-migration/scripts/upgrade_logs/run_006/upgrade.log
- SQL Fix: /Users/tri-mac/.claude/skills/odoo-db-migration/scripts/upgrade_logs/run_006/fix_run006.sql

## Next Steps
1. Review /Users/tri-mac/.claude/skills/odoo-db-migration/scripts/upgrade_logs/run_006/fix_run006.sql — edit SQL as needed for your database
2. Apply fixes: psql -h localhost -U odoo -d target_db -f /Users/tri-mac/.claude/skills/odoo-db-migration/scripts/upgrade_logs/run_006/fix_run006.sql
3. Export new dump after applying fixes
4. Re-run: ./odoo_upgrade.sh fixed_dump.sql 19.0
   (Will automatically use run_007)
