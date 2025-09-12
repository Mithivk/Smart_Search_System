import AuthForm from "../components/AuthForm";

export default function SignupPage() {
  return (
    <main className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <AuthForm type="signin" />
    </main>
  );
}
