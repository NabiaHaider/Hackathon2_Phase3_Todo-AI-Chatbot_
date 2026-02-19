'use client';

import { AuthForm } from '@/components/common/auth-form';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import * as z from 'zod';
import { formSchema } from '@/components/common/auth-form';
import Link from 'next/link';
import { registerUser } from '@/lib/api'; // Import registerUser
import { toast } from 'sonner'; // Import toast

export default function SignupPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSignup = async (values: z.infer<typeof formSchema>) => {
    setIsLoading(true);
    setError(null);

    try {
      await registerUser(values); // registerUser handles storing token
      toast.success('Signup successful! Redirecting to login...');

      setTimeout(() => {
        router.push('/login');
        router.refresh();
      }, 2000);

    } catch (e: any) {
      console.error('Signup error:', e);
      const errorMsg = e.message || 'An unexpected error occurred.';
      setError(errorMsg);
      toast.error(errorMsg);

      if (errorMsg.toLowerCase().includes('already registered') ||
          errorMsg.toLowerCase().includes('email already') ||
          errorMsg.toLowerCase().includes('exists') ||
          errorMsg.toLowerCase().includes('duplicate')) {
        setTimeout(() => {
          router.push('/login');
          router.refresh();
        }, 1500);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-[0_12px_30px_rgba(255,192,203,0.45)] p-8 transition-transform duration-500 hover:scale-105">

        <div className="text-center mb-6">
          <img
            src="/logo.png"
            alt="Logo"
            className="mx-auto h-12 w-12 rounded-full shadow-lg"
          />
          <h2 className="mt-6 text-3xl font-extrabold text-primary">
            Create your account
          </h2>
          <p className="mt-2 text-sm text-gray-500">
            Join us and start your journey 
          </p>
        </div>

        <div className="mt-8 bg-white rounded-xl p-6 shadow-inner">
          <AuthForm
            type="signup"
            onSubmit={handleSignup}
            isLoading={isLoading}
            error={error}
            inputClassName="bg-pink-50 text-black placeholder:text-primary focus:border-purple-200 focus:ring-purple-200"
            labelClassName="block text-sm font-medium text-primary mb-1"
          />
        </div>

        <div className="mt-6 text-center bg-purple-100 rounded-xl p-6 shadow-inner">
          <p className="text-sm text-primary">
            Already have an account?{' '}
            <Link href="/login" className="font-medium text-primary hover:text-purple-900">
              Login
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}