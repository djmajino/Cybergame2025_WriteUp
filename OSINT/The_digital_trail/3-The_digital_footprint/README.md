# Zadanie

EN: The suspect behind the malicious pull request appears to be a well-known figure. We need to track his digital footprint across the internet. Where else might he be active?

SK: Útočník za škodlivým pull requestom sa zdá byť známa osobnosť. Potrebujeme sledovať jeho digitálnu stopu na internete. Kde inde by mohol byť aktívny?

## Riešenie

Tak username commitera pull request sa nám teda zíde a stačí dat do google jeho nickname do úvodzoviek aby ujo google vedel, že má pracovať s presne tým stringom, ktorý sme mu zadali a nepremýšal nad iným konktextom. Takže vygooglime `"evanmassey1976"` alebo full url [Google Search](https://www.google.com/search?q=%22evanmassey1976%22)

a hneď prvý výskyt je reddit profil tohto používateľa

[evanmassey1976 (u/evanmassey1976) - Reddit](https://www.reddit.com/user/evanmassey1976/)

nemá tu nejakú bujarú aktivitu a príspevok

##### Security practices that are actually underrated

obsahuje vlajku

```
Some security practices get overlooked despite their effectiveness.

Keeping your systems updated is always the first recommendation, but there's more to it.

- - -

Creating proper network segmentation prevents lateral movement by attackers.

Every organization should implement the principle of least privilege.

Running regular security audits can identify vulnerabilities before they're exploited.

Threat modeling helps prioritize which vulnerabilities to address first.

{ Organizations should monitor network traffic for unusual patterns. }

Speaking of which, physical security is often neglected in cybersecurity planning.

0-day vulnerabilities get all the attention, but most breaches exploit known issues.

Careful documentation of your infrastructure helps identify security gaps.

1 compromised account can lead to a full network breach if proper segmentation isn't in place.

4 key areas to focus on: updates, access controls, monitoring, and employee training.

Logging everything is useless without proper analysis tools and procedures.

- Many companies invest in expensive tools but neglect basic security hygiene.

Many businesses fail to properly secure their backup systems.

3 months of logs is the minimum you should maintain for investigation purposes.

Defending against sophisticated attackers requires understanding their techniques.

1 step that's often skipped is validating that security controls actually work.

4 eyes principle (requiring two people to approve critical changes) reduces insider threats.

- Always verify that your security controls are functioning as intended.

0-trust architecture is becoming increasingly necessary in today's threat landscape.

Social engineering remains the most reliable attack vector for sophisticated threat actors.

1 phishing email can bypass millions in security investments.

Nothing replaces security awareness training for employees.

Training should be ongoing, not just an annual checkbox exercise.

- Test your employees with simulated phishing campaigns regularly.

Thorough background checks for IT staff with privileged access are essential.

Regular penetration testing reveals blind spots in your security posture.

4 weeks is too long to patch critical vulnerabilities - aim for days, not weeks.

1 unpatched server can compromise your entire infrastructure.

Look for security tools that integrate with your existing workflow, not disrupt it.

}{
```

stačí ked si vezmeme len prvý znak prvého riadku a vznikne nám vlajka.

## Vlajka

```
SK-CERT{S0C14L-M3D14-0S1NT-TR41L}
```
