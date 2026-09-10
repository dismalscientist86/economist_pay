# Historical FedScope source files

Retrieved 2026-09-09 from <https://www.opm.gov/data/datasets/>.
Economist (series 0110 / 0119) rows only; full files are in `../_downloads/`
(git-ignored). Re-create with `python src/fetch_fedscope_history.py`.

| file | OPM Files path |
| --- | --- |
| separations_FY2015-2019.zip | `611/004f4b85-fe4f-4e7d-bd7b-2d23033570cb.zip` |
| separations_FY2020-2024.zip | `652/21d85c40-bd35-4f20-9359-281a31af39b1.zip` |
| separations_202310_to_202403.zip | `773/28054cf5-0127-4039-b7ee-a49774eb3c1e.zip` |
| accessions_FY2015-2019.zip | `610/fd567924-edea-478f-bc5a-24e19efd7243.zip` |
| accessions_FY2020-2024.zip | `649/8caf0a70-9c09-4eb2-844f-71a4f21addfa.zip` |
| accessions_202310_to_202403.zip | `774/48233fa0-36c6-4397-ab63-1468daf49a8b.zip` |
| employment_199809.zip | `77/25455df4-0c25-49f3-a460-147b3aa596c8.zip` |
| employment_199909.zip | `74/70967261-28e6-4598-ad8a-69f0f6b04532.zip` |
| employment_200009.zip | `71/f74f444b-b84b-4a75-b7d5-83726b80a320.zip` |
| employment_200109.zip | `68/22fb81c4-51bb-4309-a9e5-de7fc891d299.zip` |
| employment_200209.zip | `65/a5e33b42-51aa-41f0-8d1c-0dcde6c6ff2a.zip` |
| employment_200309.zip | `62/ecdd5c00-aeda-45ff-bd74-975714ee10a6.zip` |
| employment_200409.zip | `59/b5c2a4f7-5ac5-44f7-bd3c-0f2cfb000e21.zip` |
| employment_200509.zip | `56/f00a1a8f-d865-4214-8051-049f66d322be.zip` |
| employment_200609.zip | `53/b9945224-54e1-45e3-9780-b6b36b845b4b.zip` |
| employment_200709.zip | `50/7b7655fd-b4d0-4e15-9e97-33956b8aca09.zip` |
| employment_200809.zip | `38/3653d805-eb0a-4e70-b96d-39b7c58347f0.zip` |
| employment_200909.zip | `26/f0a8eef6-a0b5-4015-a2f4-6597f1ca3ae7.zip` |
| employment_201009.zip | `172/c21d50d7-9b48-432c-a03e-96d5fb93f5fa.zip` |
| employment_201109.zip | `235/caac291b-001d-4568-a8be-96215c319fd4.zip` |
| employment_201209.zip | `253/2b43e513-cbfa-4eb5-ae9a-20e718ef1f4e.zip` |
| employment_201309.zip | `331/499b1fa1-c354-4c96-b20c-fc18a82bacb8.zip` |
| employment_201409.zip | `381/30a3741c-a24d-4f97-9a0e-e45f2ee13773.zip` |
| employment_201509.zip | `413/de1dd3f7-0c39-46ab-a1c6-848be284358b.zip` |
| employment_201609.zip | `490/ae0351fd-58d1-47d5-b1aa-2ca3bf977d30.zip` |
| employment_201709.zip | `522/e4af5225-d9fc-46fa-98f9-b360ed26840d.zip` |
| employment_201809.zip | `549/4a840c61-0c6d-41ac-8ffc-a6419b6484e0.zip` |
| employment_201909.zip | `600/52da12cd-055e-4e9b-af36-60b2ed9e7d98.zip` |
| employment_202009.zip | `621/07f71358-8972-478e-a2cb-fd02f135b7af.zip` |
| employment_202109.zip | `633/074d44a6-a8a2-4e35-9b2e-969f2cc8363f.zip` |
| employment_202209.zip | `667/fab0e970-bb13-434e-b1df-e867705c7f4e.zip` |
| employment_202309.zip | `691/41bdfdda-0ebe-4e19-81f8-5a98d55389b4.zip` |
| employment_202409.zip | `721/550993be-94ba-476c-9d66-7f7e8871b07b.zip` |

## Notes
- Pre-2025 files (`SEPDATA`/`ACCDATA`/`FACTDATA`) are comma-delimited with
  coded values; 2025-era files are pipe-delimited with text labels.
- ~550 Department of State positions were reclassified out of series 0110
  between Sep 2005 and Sep 2006, so pre-2006 headcounts run ~550 high.
- Historical `SALARY` is nominal; `analyze_history.py` deflates with CPI-U.
